#!/bin/bash

process_name="upapi"
pid_file="./$process_name.pid"

start() {
    echo "Starting $process_name..."
    daemon_cmd="$HOME/.local/bin/uvicorn app.puffy:puffy --host 127.0.0.1 --port 8000 --workers 3"
    #daemon_cmd="$HOME/.local/bin/uvicorn app.app:app --host 127.0.0.1 --port 8004 "
    $daemon_cmd & 
    echo $! > $pid_file
}

stop() {
    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        echo "Stopping $process_name with PID $pid..."
        kill $pid
        rm $pid_file
    else
        echo "$process_name is not running"
    fi
}

status() {
    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        if ps -p $pid > /dev/null; then
            echo "$process_name is running with PID $pid"
            return 0
        else
            echo "$process_name PID file exists but process is not running"
            rm $pid_file
            return 3
        fi
    else
        echo "$process_name is not running"
        return 3
    fi
}

start_if_not() {
    status
    if [ $? -eq 3 ]; then
        echo "process is down, restart it"
        start
    fi 
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    start_if_not)
        start_if_not
        ;;
    *)
        echo "Usage: $0 {start|stop|status|start_if_not}"
        exit 1
        ;;
esac

exit 0
