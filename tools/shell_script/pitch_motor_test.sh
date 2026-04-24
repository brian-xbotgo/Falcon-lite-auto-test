#!/bin/sh
FEEDBACK_FILE="/tmp/test_mqtt_feedback.bin"
touch "$FEEDBACK_FILE"

# 修复：32位十六进制补码转有符号十进制（纯十进制运算，兼容Shell）
hex_to_signed_32() {
    local hex_str=$1
    # 步骤1：先将十六进制字符串转为无符号十进制（用printf中转，避免Shell直接解析0x）
    local unsigned_val
    unsigned_val=$(printf "%d" "0x$hex_str")
    
    # 步骤2：32位有符号数最大值（2^31-1 = 2147483647），超出则转负数
    local max_signed=2147483647
    local full_32bit=4294967296
    
    if [ "$unsigned_val" -gt "$max_signed" ]; then
        unsigned_val=$((unsigned_val - full_32bit))
    fi
    echo "$unsigned_val"
}

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

# 转换结果字段（保持无符号）
result1=$(printf "%d" 0x$result1_hex)
result2=$(printf "%d" 0x$result2_hex)

# 修复：调用补码转换函数
ver1=$(hex_to_signed_32 "$ver1_hex")
ver2=$(hex_to_signed_32 "$ver2_hex")

# 计算角度（保留两位小数，兼容负数）
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