#!/usr/bin/env bash
# theAIgency launcher: runs the AI job market in the background.
#
#   ./start.sh            start (same as ./start.sh start)
#   ./start.sh stop       stop
#   ./start.sh restart    restart
#   ./start.sh status     show whether it is running
#   ./start.sh logs       follow the log
#
# Env: PORT (default 8503), HOST (default 0.0.0.0)
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8503}"
HOST="${HOST:-0.0.0.0}"
PID_FILE=".run.pid"
LOG_FILE=".run.log"

is_running() {
  [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

ensure_venv() {
  if [ ! -x .venv/bin/streamlit ]; then
    echo "Creating .venv and installing requirements…"
    python3 -m venv .venv
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -r requirements.txt
  fi
}

start() {
  if is_running; then
    echo "theAIgency already running (pid $(cat "$PID_FILE")) on port $PORT"
    return
  fi
  ensure_venv
  setsid nohup .venv/bin/streamlit run app.py --server.port "$PORT" --server.address "$HOST" \
    > "$LOG_FILE" 2>&1 < /dev/null &
  echo $! > "$PID_FILE"
  for _ in $(seq 1 30); do
    if curl -fs "http://localhost:$PORT/_stcore/health" > /dev/null 2>&1; then
      echo "theAIgency is up: http://localhost:$PORT  (pid $(cat "$PID_FILE"), log $LOG_FILE)"
      return
    fi
    is_running || { echo "Failed to start. Last log lines:"; tail -20 "$LOG_FILE"; exit 1; }
    sleep 1
  done
  echo "Started (pid $(cat "$PID_FILE")) but health check not ready yet; see $LOG_FILE"
}

stop() {
  if is_running; then
    kill "$(cat "$PID_FILE")" && echo "Stopped theAIgency (pid $(cat "$PID_FILE"))"
  else
    echo "theAIgency is not running"
  fi
  rm -f "$PID_FILE"
}

case "${1:-start}" in
  start)   start ;;
  stop)    stop ;;
  restart) stop; sleep 1; start ;;
  status)  if is_running; then echo "running (pid $(cat "$PID_FILE")) on port $PORT"; else echo "stopped"; fi ;;
  logs)    tail -f "$LOG_FILE" ;;
  *)       echo "Usage: $0 {start|stop|restart|status|logs}"; exit 1 ;;
esac
