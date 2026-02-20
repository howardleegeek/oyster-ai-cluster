#!/bin/bash

JOB_PROCESS_NAME="puffy-jobs"
JOB_SCRIPT="app/jobs/job_runner.py"
PID_FILE="./jobs.pid"
LOG_DIR="logs"

ensure_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
    fi
}

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "$JOB_PROCESS_NAME is already running with PID $PID"
            return 1
        else
            echo "Removing stale PID file"
            rm "$PID_FILE"
        fi
    fi

    echo "Starting $JOB_PROCESS_NAME..."
    ensure_log_dir
    
    nohup python "$JOB_SCRIPT" >> "$LOG_DIR/jobs.log" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    echo "$JOB_PROCESS_NAME started with PID $PID"
    echo "Logs: $LOG_DIR/jobs.log"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "$JOB_PROCESS_NAME is not running (no PID file)"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Process with PID $PID is not running"
        rm "$PID_FILE"
        return 1
    fi

    echo "Stopping $JOB_PROCESS_NAME (PID: $PID)..."
    kill $PID
    
    local count=0
    while ps -p $PID > /dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done

    if ps -p $PID > /dev/null 2>&1; then
        echo "Force killing $JOB_PROCESS_NAME (PID: $PID)..."
        kill -9 $PID
    fi

    rm "$PID_FILE"
    echo "$JOB_PROCESS_NAME stopped"
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "$JOB_PROCESS_NAME is not running"
        return 3
    fi

    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "$JOB_PROCESS_NAME is running with PID $PID"
        echo "Memory: $(ps -p $PID -o rss= | tail -1 | awk '{print $1/1024" MB"}')"
        echo "Uptime: $(ps -p $PID -o etime= | tail -1)"
        echo "Logs: $LOG_DIR/jobs.log"
        return 0
    else
        echo "PID file exists but process is not running"
        rm "$PID_FILE"
        return 3
    fi
}

restart() {
    echo "Restarting $JOB_PROCESS_NAME..."
    stop
    sleep 2
    start
}

start_if_not() {
    status
    if [ $? -eq 3 ]; then
        echo "Job is down, starting it..."
        start
    else
        echo "Job is already running"
    fi
}

tail_logs() {
    if [ -f "$LOG_DIR/jobs.log" ]; then
        tail -f "$LOG_DIR/jobs.log"
    else
        echo "Log file not found: $LOG_DIR/jobs.log"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    start_if_not)
        start_if_not
        ;;
    logs)
        tail_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|start_if_not|logs}"
        echo ""
        echo "Commands:"
        echo "  start          - Start the job process"
        echo "  stop           - Stop the job process"
        echo "  restart        - Restart the job process"
        echo "  status         - Check if job is running"
        echo "  start_if_not  - Start job only if not running"
        echo "  logs           - Tail job logs in real-time"
        exit 1
        ;;
esac

exit 0
