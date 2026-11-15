#!/bin/bash
set -euxo pipefail
mkdir -p "$EVIDENCE" "$HOME/.sugar/default/logs"
export SUGAR_PROFILE_NAME='Palette regression test'
export SUGAR_GROUP_LABELS=/usr/share/sugar/data/group-labels.defaults
export SUGAR_MIME_DEFAULTS=/usr/share/sugar/data/mime.defaults
export SUGAR_ACTIVITIES_HIDDEN=/usr/share/sugar/data/activities.hidden
export SUGAR_SCALING=72
export SUGAR_LOGGER_LEVEL=debug
export PYTHONPATH="$PWD/src"
export DISPLAY=:98
Xvfb :97 -screen 0 1600x1200x24 > "$EVIDENCE/xvfb.log" 2>&1 &
for i in $(seq 1 20); do DISPLAY=:97 xdpyinfo >/dev/null 2>&1 && break; sleep 1; done
DISPLAY=:97 Xephyr :98 -screen 1024x768 -resizeable -ac > "$EVIDENCE/xephyr.log" 2>&1 &
for i in $(seq 1 20); do xdpyinfo >/dev/null 2>&1 && break; sleep 1; done
gsettings set org.sugarlabs.user group-label 'Adult'
gsettings set org.sugarlabs.collaboration jabber-server ''
sugar > "$EVIDENCE/sugar-stdout.log" 2>&1 &
SUGAR_PID=$!
cleanup() { cat "$EVIDENCE/xephyr.log"; cat "$EVIDENCE/sugar-stdout.log"; cp -r "$HOME/.sugar/default/logs" "$EVIDENCE/profile-logs" || true; kill "$SUGAR_PID" || true; }
trap cleanup EXIT
sleep 25
kill -0 "$SUGAR_PID" || { cat "$EVIDENCE/sugar-stdout.log"; cat "$HOME/.sugar/default/logs/shell.log"; exit 1; }
pgrep -af 'jarabe.main|metacity' | tee "$EVIDENCE/desktop-processes.txt"
import -window root "$EVIDENCE/01-sugar-home.png"
sugar-launch org.laptop.Terminal > "$EVIDENCE/terminal-launch.log" 2>&1 &
sleep 15
xdotool search --onlyvisible --name 'Terminal' getwindowname | tee "$EVIDENCE/terminal-window.txt"
xdotool mousemove 990 28
sleep 3
import -window root "$EVIDENCE/02-stop-at-1024.png"
xdotool mousemove 500 400
sleep 1
xrandr -q | tee "$EVIDENCE/xrandr-before.txt"
xrandr --output default --mode 1280x720
sleep 5
xrandr -q | tee "$EVIDENCE/xrandr-after.txt"
xdotool mousemove 1248 28
sleep 3
import -window root "$EVIDENCE/03-stop-at-1280.png"
