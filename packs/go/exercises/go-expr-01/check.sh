#!/bin/bash
cd ~/exercise

EXPECTED=""
for i in 1 2 3 4 5; do
    for j in 1 2 3 4 5; do
        EXPECTED="${EXPECTED}${i} x ${j} = $((i*j))\n"
    done
done
EXPECTED=$(printf "$EXPECTED" | head -c -1)  # trim trailing newline

GOT=$(go run main.go 2>&1)

if [ "$GOT" = "$EXPECTED" ]; then
    echo "OK: таблица умножения выведена верно"
else
    echo "FAIL: вывод не совпадает"
    echo "Ожидается:"
    printf "$EXPECTED\n"
    echo "Получено:"
    echo "$GOT"
    exit 1
fi
