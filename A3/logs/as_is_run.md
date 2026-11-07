# Попытка запуска неизменённого кода в Colab

Блокнот с выполненными ячейками и выводами: https://colab.research.google.com/drive/10niEqlOf72tR05LYKT9ISfawULAziJbw

Результат: код не дошёл до обучения. Метрик accuracy и времени обучения нет. Ни наличие GPU, ни успешная установка зависимостей не означают успешного воспроизведения.

## Фактическое окружение

По nvidia-smi: Tesla T4, 15360 MiB, драйвер 580.82.07. Показанная драйвером максимальная версия CUDA — 13.0; это не подтверждение CUDA, используемой TensorFlow. Python 3.13.16; pip freeze показывает TensorFlow 2.21.0, Keras 3.13.2, NumPy 2.4.6. Наличие cuDNN-пакетов в окружении не доказывает загрузку их TensorFlow.

Исходники: Google Research, commit `1f17279d282e729ee29e80a2f750cfbffc4b8500`. `git diff --exit-code` после попытки вернул 0. Это повторная реализация с участием автора статьи, а не подтверждённые исходники экспериментов ICLR 2019.

## Попытки

Команда: `/usr/bin/python3 -m lottery_ticket.mnist_fc.runners.lottery_experiment --output_dir=/content/A3_outputs`.

Первая попытка: 7 ноября 2026, 22:28:20.390390 UTC (8 ноября, 01:28:20 по Москве). Длительность 0.143261386 с, exit code 1: `ModuleNotFoundError: No module named 'fire'`.

Затем выполнена установка заявленных зависимостей: `/usr/bin/python3 -m pip install /content/lottery_ticket`. Начало 22:28:43.135685 UTC, длительность 6.796336468 с, exit code 0. Исходники не изменялись.

Повторная попытка: начало 22:28:51.060170 UTC (8 ноября, 01:28:51 по Москве), длительность 5.954783332 с, exit code 1:

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/content/lottery_ticket/mnist_fc/runners/lottery_experiment.py", line 22, in <module>
    from lottery_ticket.mnist_fc import lottery_experiment
  File "/content/lottery_ticket/mnist_fc/lottery_experiment.py", line 29, in <module>
    from lottery_ticket.mnist_fc import constants
  File "/content/lottery_ticket/mnist_fc/constants.py", line 31, in <module>
    FASHIONMNIST_LOCATION = locations.FASHIONMNIST_LOCATION
AttributeError: module 'lottery_ticket.mnist_fc.locations' has no attribute 'FASHIONMNIST_LOCATION'
```

## Сохранение

Команды, stdout/stderr, длительности и exit codes сохранены в `/content/A3_evidence` в Colab; архив `/content/A3_evidence.zip` создан. Полный pip freeze до/после установки и выводы попыток видны в блокноте. Автоматический перенос архива и экспорт блокнота на локальный диск через браузер не подтверждены: ожидание скачивания завершилось по таймауту. Этот файл — запись проверенных выводов, а не копия полного архива логов. Содержимое `/content` временное; необходимо сохранить архив до удаления runtime.

В первой попытке MNIST не скачивался: импорт остановился раньше. Затем выполнен отдельный успешный пилот с правками, описанный ниже.

## Отдельный пилот с правками совместимости

Начало процесса: 7 ноября 2026, 22:38:47.871768 UTC (8 ноября 01:38:47 МСК). Код скопирован в `/content/A3_compat/lottery_ticket`. Импорты заменены на TensorFlow compat.v1 с отключением v2 behavior, отсутствующий fashion-путь задан, tf.contrib initializer заменён на Gaussian Glorot compat, исправлены API tf.data и бинарные режимы NumPy-файлов. Полный diff: `compatibility.patch`.

Вызван скрипт `/content/A3_compat/pilot.py` из рабочего каталога `/content/A3_compat`; он скачивает MNIST через tensorflow.keras, сохраняет его для upstream DatasetMnist и вызывает `lottery_experiment.train(..., iterations=0, train_order_seed=0)`. `iterations=0` здесь означает отсутствие раундов pruning после плотной модели, а не нулевое обучение. Использован default TRAINING_LEN 50 000.

Exit code 0. Время функции обучения — 164.00720671099998 с. Final test accuracy 0.9796000123023987, loss 0.07163893431425095. Счётчик 50 000, фактических строк train — 49 947. GPU подтверждена TensorFlow: Tesla T4, compute capability 7.5, выделено 13757 MB. Среда осталась Python 3.13.16, TF 2.21.0, Keras 3.13.2, NumPy 2.4.6.

SGD 0,1, batch 64, train 60 000, test 10 000; validation нет. Это только плотный пилот; early-stopping metric и результат Figure 4a не заявляются. Код reset_default_graph не гарантирует сохранение заданного в launcher TF seed, поэтому пилот нельзя выдавать за полностью детерминированный seed 0. Обе особенности учтены в плане основных экспериментов.

Полные выводы доступны в ячейках 0–7 Colab. Исходные файлы, train/test-логи и веса собраны в `/content/A3_evidence_complete.zip`. Архив не перенесён на локальный диск автоматически из-за ограничения браузера. `pilot_summary.json` — перенос наблюдённых чисел; источники сохраняются в Colab.
