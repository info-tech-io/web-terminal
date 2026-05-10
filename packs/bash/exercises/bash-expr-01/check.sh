#!/bin/bash
# Проверяет, что solution.sh выводит число > 0 (точное значение зависит от образа).
cd ~/exercise

if [ ! -f solution.sh ]; then
    echo "FAIL: файл solution.sh не найден"
    exit 1
fi

chmod +x solution.sh
output=$(bash solution.sh 2>&1)

if ! echo "$output" | grep -qE '^[0-9]+$'; then
    echo "FAIL: ожидается одно число, получено: $output"
    exit 1
fi

count=$output
if [ "$count" -le 0 ]; then
    echo "FAIL: число должно быть больше 0, получено: $count"
    exit 1
fi

echo "OK: найдено $count исполняемых файлов в /usr/bin"
