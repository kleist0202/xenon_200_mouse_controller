EVENT_FILE=$(cat /proc/bus/input/devices | grep -A4 "SINOWEALTH Game Mouse Keyboard" | awk '/Handlers/{print $4}')
./daemon $EVENT_FILE
