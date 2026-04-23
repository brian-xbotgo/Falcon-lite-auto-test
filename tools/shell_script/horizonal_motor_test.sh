#!/bin/sh
FEEDBACK_FILE="/tmp/test_mqtt_feedback.bin"
touch "$FEEDBACK_FILE"

get_hex() {
    hexdump "$1" | awk '{for(i=2;i<=NF;i++) printf $i}' | tr -d ' \n'
}

printf '\x2A\x00\x00\x23\x28\x00\x02' | mosquitto_pub -h localhost -t AQR -s
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

# 解析字段
result1_hex=${variable1:0:4}
hor1_hex=${variable1:4:8}
result2_hex=${variable2:0:4}
hor2_hex=${variable2:4:8}

result1=$(printf "%d" 0x$result1_hex)
result2=$(printf "%d" 0x$result2_hex)
hor1=$(printf "%d" 0x$hor1_hex)
hor2=$(printf "%d" 0x$hor2_hex)

hor1_angle=$(echo "scale=2; $hor1 / 100" | bc)
hor2_angle=$(echo "scale=2; $hor2 / 100" | bc)

# 逻辑：两次不同=normal；相同=error；result≠0=error
motor_status="error"
if [ "$result1" -eq 0 ] && [ "$result2" -eq 0 ]; then
    if [ "$hor1" -ne "$hor2" ]; then
        motor_status="normal"
    fi
fi

echo "motor status:$motor_status"
echo "first horizontal angle:$hor1_angle"
echo "second horizontal angle:$hor2_angle"

printf '\x2B' | mosquitto_pub -h localhost -t AQR -s