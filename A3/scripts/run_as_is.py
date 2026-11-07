"""Run from /content in Colab. Records failures without modifying upstream."""
import datetime
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path.cwd()
OUT = ROOT / 'A3_evidence'
OUT.mkdir(exist_ok=True)
SHA = '1f17279d282e729ee29e80a2f750cfbffc4b8500'

def capture(name, command):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tick = time.perf_counter()
    r = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    (OUT / (name + '.log')).write_text(r.stdout)
    (OUT / (name + '.json')).write_text(json.dumps({
        'command': command, 'start_utc': start,
        'end_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'elapsed_seconds': time.perf_counter()-tick, 'exit_code': r.returncode
    }, indent=2))
    print(name, r.returncode, r.stdout[-4000:])
    return r.returncode

if __name__ == '__main__':
    capture('python', [sys.executable, '--version'])
    capture('gpu', ['nvidia-smi'])
    capture('packages_before', [sys.executable, '-m', 'pip', 'freeze'])
    source = ROOT / 'lottery_ticket'
    if source.exists():
        raise SystemExit('Use a fresh directory; existing source is not overwritten.')
    if capture('clone', ['git', 'clone', 'https://github.com/google-research/lottery-ticket-hypothesis.git', str(source)]):
        raise SystemExit(1)
    if capture('checkout', ['git', '-C', str(source), 'checkout', SHA]):
        raise SystemExit(1)
    capture('commit', ['git', '-C', str(source), 'rev-parse', 'HEAD'])
    capture('install', [sys.executable, '-m', 'pip', 'install', str(source)])
    capture('packages_after', [sys.executable, '-m', 'pip', 'freeze'])
    code = capture('unchanged_attempt', [sys.executable, '-m',
        'lottery_ticket.mnist_fc.runners.lottery_experiment',
        '--output_dir=' + str(ROOT/'A3_outputs')])
    capture('diff', ['git', '-C', str(source), 'diff', '--exit-code'])
    raise SystemExit(code)
