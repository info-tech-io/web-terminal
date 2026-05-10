#!/bin/bash
cd ~/exercise
PASS=0; FAIL=0

run() {
    local desc="$1"; shift
    local expected="$1"; shift
    local got
    got=$("$@" 2>/dev/null)
    local exit_ok=$?
    if [ "$got" = "$expected" ]; then
        echo "OK: $desc"
        PASS=$((PASS+1))
    else
        echo "FAIL: $desc — ожидается '$expected', получено '$got'"
        FAIL=$((FAIL+1))
    fi
}

run_exit1() {
    local desc="$1"; shift
    "$@" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "OK: $desc"
        PASS=$((PASS+1))
    else
        echo "FAIL: $desc — ожидается exit 1"
        FAIL=$((FAIL+1))
    fi
}

EXPECTED=$(wc -w < sample.txt | tr -d ' ')

run "подсчёт слов в sample.txt" "$EXPECTED" bash count_words.sh sample.txt
run_exit1 "нет аргумента → exit 1" bash count_words.sh
run_exit1 "несуществующий файл → exit 1" bash count_words.sh __no_such_file__.txt

echo "---"
echo "Пройдено: $PASS / $((PASS+FAIL))"
[ "$FAIL" -eq 0 ]
