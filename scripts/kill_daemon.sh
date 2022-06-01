PID=$(ps -C daemon -o "pid" | sed -n '2p')
kill $PID
