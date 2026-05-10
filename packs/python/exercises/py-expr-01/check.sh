#!/bin/bash
cd ~/exercise
EXPECTED="[1, 9, 25, 49, 81, 121, 169, 225, 289, 361]"
GOT=$(python3 solution.py 2>&1)

if [ "$GOT" = "$EXPECTED" ]; then
    echo "OK: вывод совпадает"
else
    echo "FAIL: ожидается:"
    echo "  $EXPECTED"
    echo "получено:"
    echo "  $GOT"
    exit 1
fi
