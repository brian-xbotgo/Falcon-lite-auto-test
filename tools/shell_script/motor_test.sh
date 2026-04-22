#!/bin/sh

FEEDBACK_FILE="/tmp/test_mqtt_feedback.bin"
touch "$FEEDBACK_FILE"

get_hex() {
    hexdump "$1" | awk '{for(i=2;i<=NF;i++) printf $i}' | tr -d ' \n'
}

printf '\x00\x01' | mosquitto_pub -h localhost -t AYR -s
mosquitto_sub -h 127.0.0.1 -t BXA -C 1 -W 20 > "$FEEDBACK_FILE" &
sleep 0.5
mosquitto_pub -h 127.0.0.1 -t BXR -n
sleep 0.5

variable1=$(get_hex "$FEEDBACK_FILE")

mosquitto_sub -h 127.0.0.1 -t BXA -C 1 -W 20 > "$FEEDBACK_FILE" &
sleep 0.5
mosquitto_pub -h 127.0.0.1 -t BXR -n
sleep 0.5

variable2=$(get_hex "$FEEDBACK_FILE")

echo "first angle:$variable1"
echo "second angle:$variable2"

printf "\x00\x02" | mosquitto_pub -h localhost -t AYR -s
