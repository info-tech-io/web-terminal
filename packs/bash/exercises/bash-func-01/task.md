══════════════════════════════════════════════════
  Задание: Подсчёт слов
══════════════════════════════════════════════════

Напиши скрипт count_words.sh, который:
  1. Принимает путь к файлу первым аргументом ($1)
  2. Выводит количество слов в файле
  3. Если файл не передан или не существует — выводит
     сообщение об ошибке в stderr и завершается с кодом 1

Примеры:
  $ bash count_words.sh sample.txt
  17

  $ bash count_words.sh
  Error: no file provided
  (exit code 1)

  $ bash count_words.sh missing.txt
  Error: file not found: missing.txt
  (exit code 1)

Файл для работы: ~/exercise/count_words.sh
Тестовые данные: ~/exercise/sample.txt

Для проверки введи команду: check
══════════════════════════════════════════════════
