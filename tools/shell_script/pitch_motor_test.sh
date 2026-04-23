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

# 解析字段
result1_hex=${variable1:0:4}
ver1_hex=${variable1:12:8}
result2_hex=${variable2:0:4}
ver2_hex=${variable2:12:8}

result1=$(printf "%d" 0x$result1_hex)
result2=$(printf "%d" 0x$result2_hex)
ver1=$(printf "%d" 0x$ver1_hex)
ver2=$(printf "%d" 0x$ver2_hex)

ver1_angle=$(echo "scale=2; $ver1 / 100" | bc)
ver2_angle=$(echo "scale=2; $ver2 / 100" | bc)
printf "\x00\x02" | mosquitto_pub -h localhost -t AYR -s
# 逻辑：两次不同=normal；相同=error；result≠0=error
motor_status="error"
if [ "$result1" -eq 0 ] && [ "$result2" -eq 0 ]; then
    if [ "$ver1" -ne "$ver2" ]; then
        motor_status="normal"
    fi
fi

echo "motor status:$motor_status"
echo "first vertical angle:$ver1_angle"
echo "second vertical angle:$ver2_angle"

printf '\x04\x00' | mosquitto_pub -h localhost -t AYR -s