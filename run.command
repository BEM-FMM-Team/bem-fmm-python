#!/usr/bin/env bash
# run app

source ./scripts/setup.sh

echo
echo "-- running app --"

if [ -x "$VENV_DIR/bin/tms_coil_navigator" ]; then
    echo "running tms_coil_navigator"
    "$VENV_DIR/bin/tms_coil_navigator" "$@"
    status=$?
    if [ $status -eq 0 ]; then
        exit 0
    fi
    echo "binary failed, running module directly..."
fi

echo "running module directly..."
"$VENV_DIR/bin/python" -m apps.gui.__main__ "$@"
exit $?
