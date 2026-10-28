#!/bin/bash
set -u
launcher=${ATSPI_LAUNCHER:-/usr/libexec/at-spi-bus-launcher}
"$launcher" --launch-immediately >/tmp/sugar-proof-atspi.log 2>&1 &
p=$!
trap 'kill "$p" 2>/dev/null; wait "$p" 2>/dev/null' EXIT
sleep 1
/usr/bin/python3 -m sugar3.test.discover tests
rc=$?
exit "$rc"
