"""Create a separate TF2-compat copy. Never modifies the upstream directory."""
import argparse
import difflib
from pathlib import Path
import shutil

def prepare(source, target, patch_path):
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    patch = []
    for f in target.rglob('*.py'):
        old = f.read_text()
        new = old.replace('import tensorflow as tf',
                          'import tensorflow.compat.v1 as tf\ntf.disable_v2_behavior()')
        new = new.replace('FASHIONMNIST_LOCATION = locations.FASHIONMNIST_LOCATION',
                          "FASHIONMNIST_LOCATION = 'data/fashionmnist'")
        new = new.replace('tf.contrib.layers.xavier_initializer(\n              uniform=False)',
                          'tf.glorot_normal_initializer()')
        new = new.replace('self._dataset.make_initializable_iterator()',
                          'tf.data.make_initializable_iterator(self._dataset)')
        new = new.replace('self._train.dataset.output_types',
                          'tf.data.get_output_types(self._train.dataset)')
        new = new.replace('self._train.dataset.output_shapes',
                          'tf.data.get_output_shapes(self._train.dataset)')
        new = new.replace("k + '.npy'), 'w'", "k + '.npy'), 'wb'")
        new = new.replace('os.path.join(filename, basename))',
                          "os.path.join(filename, basename), 'rb')")
        if old != new:
            rel = str(f.relative_to(target))
            patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                         fromfile='a/'+rel, tofile='b/'+rel))
            f.write_text(new)
    patch_path.write_text(''.join(patch))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    parser.add_argument('patch', type=Path)
    args = parser.parse_args()
    prepare(args.source, args.target, args.patch)
