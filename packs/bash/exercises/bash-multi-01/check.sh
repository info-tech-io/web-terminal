#!/bin/bash
cd ~/exercise
PASS=0; FAIL=0
rm -f app.log

check_ok() {
    local desc="$1"; PASS=$((PASS+1)); echo "OK: $desc"
}
check_fail() {
    local desc="$1"; FAIL=$((FAIL+1)); echo "FAIL: $desc"
}

# log.sh записывает строки
bash log.sh INFO  "Тест старт"
bash log.sh WARN  "Предупреждение"
bash log.sh ERROR "Ошибка"

if [ ! -f app.log ]; then
    check_fail "app.log не создан"
else
    check_ok "app.log создан"

    lines=$(wc -l < app.log)
    if [ "$lines" -ge 3 ]; then
        check_ok "записано $lines строк"
    else
        check_fail "ожидается ≥3 строк в app.log, найдено: $lines"
    fi

    if grep -q "\[INFO\]"  app.log && \
       grep -q "\[WARN\]"  app.log && \
       grep -q "\[ERROR\]" app.log; then
        check_ok "уровни INFO/WARN/ERROR присутствуют"
    else
        check_fail "не все уровни найдены в app.log"
    fi

    if grep -qE '\[[0-9]{4}-[0-9]{2}-[0-9]{2}' app.log; then
        check_ok "формат даты присутствует"
    else
        check_fail "формат даты не найден (ожидается [YYYY-MM-DD ...])"
    fi
fi

# tail_log.sh
if bash tail_log.sh 2 | grep -q "Ошибка"; then
    check_ok "tail_log.sh показывает последние строки"
else
    check_fail "tail_log.sh не работает корректно"
fi

# tail_log.sh без аргумента (дефолт 10)
bash tail_log.sh >/dev/null 2>&1 && check_ok "tail_log.sh без аргумента работает" \
                                 || check_fail "tail_log.sh без аргумента завершился с ошибкой"

echo "---"
echo "Пройдено: $PASS / $((PASS+FAIL))"
[ "$FAIL" -eq 0 ]
