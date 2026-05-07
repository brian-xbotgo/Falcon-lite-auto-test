#!/bin/bash
# =========================================================
# RV1126B/RK3576 Automated Test Menu
# All automated test cases integrated - SELF CONTAINED
# Updated: Added SD Card Check, Record Mark, M-Button Record tests
#
# Required external tools (only these need to be uploaded):
#   /tmp/record_test
#   /tmp/mp4info_rk3576  (for Falcon)
#   /tmp/mp4info_rv1126b (for Falcon-Air)
# =========================================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Tool paths
RECORD_TEST="/tmp/record_test"
IMG_CHECK="/tmp/IMG_check.sh"
HORIZONTAL_TEST="/tmp/horizonal_motor_test.sh"
PITCH_TEST="/tmp/pitch_motor_test.sh"
SDCARD_TEST="/tmp/sdcard_check.sh"

# =========================================================
# Embedded helper scripts - auto-generated on run
# =========================================================

generate_helper_scripts() {
    # Generate IMG_check.sh
    cat > "$IMG_CHECK" << 'EOF'
#!/bin/bash
get_file_size() {
    wc -c < "$1" 2>/dev/null || echo 0
}
read_hex() {
    local file="$1"
    local offset="$2"
    local count="$3"
    dd if="$file" bs=1 skip="$offset" count="$count" 2>/dev/null | xxd -p 2>/dev/null | tr -d '\n'
}
get_jpg_resolution() {
    local file="$1"
    local offset=2
    local file_size=$(get_file_size "$file")
    while [ $offset -lt $file_size ]; do
        local marker=$(read_hex "$file" $offset 2)
        [ -z "$marker" ] && break
        if [ "$marker" = "ffc0" ] || [ "$marker" = "ffc2" ]; then
            local data=$(read_hex "$file" $((offset + 5)) 4)
            if [ ${#data} -eq 8 ]; then
                local height=$(printf "%d" "0x${data:0:4}" 2>/dev/null)
                local width=$(printf "%d" "0x${data:4:4}" 2>/dev/null)
                if [ -n "$width" ] && [ -n "$height" ] && [ "$width" -gt 0 ] && [ "$height" -gt 0 ]; then
                    echo "${width}x${height}"
                    return 0
                fi
            fi
            return 1
        fi
        if [[ "$marker" =~ ^ff(d[0-7]|01|d9) ]]; then
            offset=$((offset + 2))
        else
            local len_hex=$(read_hex "$file" $((offset + 2)) 2)
            [ -z "$len_hex" ] && break
            local segment_len=$(printf "%d" "0x$len_hex" 2>/dev/null || echo 0)
            [ $segment_len -lt 2 ] && break
            offset=$((offset + 2 + segment_len))
        fi
    done
    return 1
}
check_jpg() {
    local file="$1"
    local file_size=$(get_file_size "$file")
    if [ -z "$file_size" ] || [ "$file_size" -lt 100 ]; then
        echo "status:corruption(The file is too small.)"
        return 1
    fi
    local head=$(read_hex "$file" 0 2)
    if [ "$head" != "ffd8" ]; then
        echo "status:corruption(Invalid JPG file header)"
        return 1
    fi
    local resolution=$(get_jpg_resolution "$file")
    if [ $? -eq 0 ]; then
        echo "status:normal"
        echo "resolution:$resolution"
        return 0
    else
        echo "status:corruption(Unable to recognize the image data)"
        return 1
    fi
}
if [ $# -eq 1 ]; then
    echo "format:JPG"
    check_jpg "$1"
else
    echo "Usage:$0 <image path>"
fi
EOF
    
    # Generate horizonal_motor_test.sh
    cat > "$HORIZONTAL_TEST" << 'EOF'
#!/bin/sh
FEEDBACK_FILE="/tmp/test_mqtt_feedback.bin"
touch "$FEEDBACK_FILE"
# 修复：32位十六进制补码转有符号十进制（纯十进制运算）
hex_to_signed_32() {
    local hex_str=$1
    local unsigned_val
    unsigned_val=$(printf "%d" "0x$hex_str")
    
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
# 转换结果字段（保持无符号）
result1=$(printf "%d" 0x$result1_hex)
result2=$(printf "%d" 0x$result2_hex)
# 修复：调用补码转换函数
hor1=$(hex_to_signed_32 "$hor1_hex")
hor2=$(hex_to_signed_32 "$hor2_hex")
# 计算角度（保留两位小数）
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
sleep 3
EOF
    
    # Generate pitch_motor_test.sh
    cat > "$PITCH_TEST" << 'EOF'
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
sleep 3
EOF
    
    # Generate sdcard_check.sh
    cat > "$SDCARD_TEST" << 'EOF'
#!/bin/sh
OUTPUT_FILE="/tmp/sdcard_output.bin"
touch "$OUTPUT_FILE"

# MQTT subscribe and publish for SD card info
mosquitto_sub -h 127.0.0.1 -p 1883 -t 'CSA' -C 1 -W 60 > "$OUTPUT_FILE" &
SUB_PID=$!
sleep 0.5
mosquitto_pub -h 127.0.0.1 -p 1883 -t 'CSR' -n
wait $SUB_PID

# Check if we got any data
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "SD card not mounted"
    exit 1
fi

# Parse hex data (hexdump format: space separated hex pairs)
HEX_PARTS=$(hexdump "$OUTPUT_FILE" | awk '{for(i=2;i<=NF;i++) printf $i" "; print ""}' | tr -d '\n')

# Convert space separated parts to array
IFS=' ' read -ra PARTS <<< "$HEX_PARTS"

# Initialize raw bytes array (9 bytes)
RAW_BYTES=([0]=0 [1]=0 [2]=0 [3]=0 [4]=0 [5]=0 [6]=0 [7]=0 [8]=0)

# Parse hex parts according to Python logic
if [ ${#PARTS[@]} -ge 1 ]; then
    # First part: a701 -> BYTE0=01, BYTE4=a7
    PART1=${PARTS[0]}
    RAW_BYTES[0]=$((16#${PART1:2:2}))  # 01
    RAW_BYTES[4]=$((16#${PART1:0:2}))  # a7
fi

if [ ${#PARTS[@]} -ge 2 ]; then
    # Second part: 0004 -> BYTE1=00, BYTE2=00, BYTE3=04
    PART2=${PARTS[1]}
    RAW_BYTES[1]=$((16#${PART2:0:2}))  # 00
    RAW_BYTES[2]=0                      # Fixed 00
    RAW_BYTES[3]=$((16#${PART2:2:2}))  # 04
fi

if [ ${#PARTS[@]} -ge 3 ]; then
    # Third part: a600 -> BYTE5=00, BYTE8=a6
    PART3=${PARTS[2]}
    RAW_BYTES[5]=$((16#${PART3:2:2}))  # 00
    RAW_BYTES[8]=$((16#${PART3:0:2}))  # a6
fi

if [ ${#PARTS[@]} -ge 4 ]; then
    # Fourth part: 0004 -> BYTE6=00, BYTE7=04
    PART4=${PARTS[3]}
    RAW_BYTES[6]=$((16#${PART4:0:2}))  # 00
    RAW_BYTES[7]=$((16#${PART4:2:2}))  # 04
fi

# Extract final values
BYTE0=${RAW_BYTES[0]}  # Mount status

# Total capacity: bytes 1-4 (big-endian)
BYTE1_4=$(( (RAW_BYTES[1] << 24) | (RAW_BYTES[2] << 16) | (RAW_BYTES[3] << 8) | RAW_BYTES[4] ))

# Available capacity: bytes 5-8 (big-endian)
BYTE5_8=$(( (RAW_BYTES[5] << 24) | (RAW_BYTES[6] << 16) | (RAW_BYTES[7] << 8) | RAW_BYTES[8] ))

# Check mount status
if [ "$BYTE0" -eq 0 ]; then
    echo "SD card not mounted"
    exit 1
fi

# Calculate capacities (unit: 0.1GB)
TOTAL_GB=$(echo "scale=1; $BYTE1_4 / 10" | bc)
AVAILABLE_GB=$(echo "scale=1; $BYTE5_8 / 10" | bc)

echo "SD card mounted, total capacity: ${TOTAL_GB}GB, available: ${AVAILABLE_GB}GB"
exit 0
EOF

    # Make all scripts executable
    chmod +x "$IMG_CHECK" "$HORIZONTAL_TEST" "$PITCH_TEST" "$SDCARD_TEST"
}

# Cleanup function
cleanup() {
    rm -f "$IMG_CHECK" "$HORIZONTAL_TEST" "$PITCH_TEST" "$SDCARD_TEST"
    echo -e "\nCleaned up temporary scripts"
}

# Generate helper scripts on startup
generate_helper_scripts

# Register cleanup trap
trap cleanup EXIT

# Detect platform to select correct mp4info
# if [ -f "/userdata/cpuinfo.txt" ]; then
#     if grep -q "Falcon-Air" /oem/usr/conf/version.txt 2>/dev/null; then
#         MP4INFO="/tmp/mp4info_rv1126b"
#         PLATFORM="Falcon-Air"
#     else
#         MP4INFO="/tmp/mp4info_rk3576"
#         PLATFORM="Falcon"
#     fi
# else
#     MP4INFO="/tmp/mp4info_rk3576"
#     PLATFORM="Generic"
# fi

MP4INFO="/tmp/mp4info_rv1126b"
PLATFORM="Falcon-Air"
# =========================================================
# Utility functions
# =========================================================

check_tool() {
    local tool_path="$1"
    if [ ! -x "$tool_path" ]; then
        echo -e "${YELLOW}Warning: $tool_path not found, please upload tools first${NC}"
        return 1
    fi
    return 0
}

# 智能文件验证函数（兼容Android设备）
validate_device_file() {
    local file_path="$1"
    local operation_start="$2"
    local max_age="${3:-300}"  # 默认5分钟

    # 检查文件是否存在
    if [ ! -f "$file_path" ]; then
        echo "File does not exist: $file_path"
        return 1
    fi

    # 提取文件名
    local filename=$(basename "$file_path")
    local file_timestamp=""

    # 从文件名解析时间戳（VID_20260428_105137_01.mp4 或 IMG_20260428_105137_01.jpg）
    if echo "$filename" | grep -qE "(VID|IMG)_20[0-9]{6}_[0-9]{6}"; then
        # 提取日期和时间部分
        local date_part=$(echo "$filename" | sed -n 's/.*_\(20[0-9]\{6\}\)_.*/\1/p')
        local time_part=$(echo "$filename" | sed -n 's/.*_20[0-9]\{6\}_\([0-9]\{6\}\)_.*/\1/p')

        if [ -n "$date_part" ] && [ -n "$time_part" ]; then
            # 构造日期时间字符串并转换为Unix时间戳
            local datetime_str="${date_part}${time_part}"
            # 使用date命令解析（如果可用）
            if command -v date >/dev/null 2>&1; then
                file_timestamp=$(date -d "${datetime_str:0:4}-${datetime_str:4:2}-${datetime_str:6:2} ${datetime_str:8:2}:${datetime_str:10:2}:${datetime_str:12:2}" +%s 2>/dev/null)
            fi

            # 如果date命令不可用，手动计算（简化版）
            if [ -z "$file_timestamp" ]; then
                # 简单的近似计算：距离2020-01-01的天数 * 86400 + 小时*3600 + 分钟*60 + 秒
                local year=$((10#${datetime_str:0:4}))
                local month=$((10#${datetime_str:4:2}))
                local day=$((10#${datetime_str:6:2}))
                local hour=$((10#${datetime_str:8:2}))
                local minute=$((10#${datetime_str:10:2}))
                local second=$((10#${datetime_str:12:2}))

                # 简化的时间戳计算（近似值）
                local days_since_2020=$(( (year-2020)*365 + (month-1)*30 + day - 1 ))
                file_timestamp=$(( 1577836800 + days_since_2020*86400 + hour*3600 + minute*60 + second ))
            fi
        fi
    fi

    # 如果文件名解析失败，尝试使用系统命令
    if [ -z "$file_timestamp" ]; then
        # 尝试多种方法获取文件时间
        file_timestamp=$(ls -l --time-style=+%s "$file_path" 2>/dev/null | awk '{print $6}') ||
                      $(stat -c %Y "$file_path" 2>/dev/null) ||
                      $(date -r "$file_path" +%s 2>/dev/null) ||
                      ""
    fi

    # 如果仍然无法获取时间戳，使用基本检查（文件存在即通过）
    if [ -z "$file_timestamp" ] || [ "$file_timestamp" = "0" ]; then
        echo "Unable to get file timestamp, using basic validation (file exists)"
        echo "File validation passed (basic check)"
        return 0
    fi

    # 获取设备当前时间
    local device_time
    device_time=$(date +%s 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$device_time" ]; then
        # 如果无法获取设备时间，使用操作开始时间进行基本验证
        local current_time=$(date +%s 2>/dev/null || echo "$operation_start")
        local time_since_operation=$((current_time - operation_start))

        if [ $time_since_operation -lt 0 ]; then
            echo "Operation time error"
            return 1
        fi

        if [ $time_since_operation -gt $max_age ]; then
            echo "File generation time exceeds limit: ${time_since_operation}s (max allowed ${max_age}s)"
            return 1
        fi

        echo "File validation passed, operation time elapsed: ${time_since_operation}s"
        return 0
    fi

    # 计算时间差
    local time_diff=$((device_time - file_timestamp))

    # 验证文件是否在合理时间内生成
    if [ $time_diff -lt 0 ]; then
        echo "File time error: file time is later than current time by ${time_diff#-}s"
        return 1
    fi

    if [ $time_diff -gt $max_age ]; then
        echo "File generation time exceeds limit: ${time_diff}s (max allowed ${max_age}s)"
        return 1
    fi

    echo "File validation passed, time difference: ${time_diff}s"
    return 0
}

press_any_key() {
    read -n 1 -s -r -p "Press any key to continue..."
    echo
}

# =========================================================
# Test Case Implementations
# =========================================================

test_video_record() {
    echo -e "\n${YELLOW}=== Video Record Test ===${NC}"
    
    check_tool "$RECORD_TEST" || return
    check_tool "$MP4INFO" || return
    
    echo "Starting video recording..."
    $RECORD_TEST mute 0
    sleep 1
    $RECORD_TEST record 0 1 0 0
    sleep 5
    $RECORD_TEST record 3 1 0 0
    sleep 15
    
    # Get latest video file
    VIDEO_FILE=$(ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 2>/dev/null | head -1)

    if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}FAIL: No video file generated${NC}"
        press_any_key
        return
    fi

    echo "Generated file: $VIDEO_FILE"

    # Validate file timestamp (within 5 minutes)
    if ! validate_device_file "$VIDEO_FILE" "$(date +%s)" 300; then
        echo -e "${RED}FAIL: File validation failed${NC}"
        press_any_key
        return
    fi
    
    # Analyze with mp4info
    MP4_OUTPUT=$($MP4INFO "$VIDEO_FILE" 2>&1)
    
    # Check video track
    if echo "$MP4_OUTPUT" | grep -q "1.*video.*H264"; then
        echo -e "${GREEN}PASS: Video record test passed${NC}"
        echo "Details: $(echo "$MP4_OUTPUT" | grep "1.*video")"
        rm -f "$VIDEO_FILE"
    else
        echo -e "${RED}FAIL: Video record test failed${NC}"
        echo "Output: $MP4_OUTPUT"
    fi
    
    press_any_key
}

test_audio_record() {
    echo -e "\n${YELLOW}=== Audio Record Test ===${NC}"
    
    check_tool "$RECORD_TEST" || return
    check_tool "$MP4INFO" || return
    
    echo "Starting audio recording..."
    $RECORD_TEST mute 0
    sleep 1
    $RECORD_TEST record 0 1 0 0
    sleep 5
    $RECORD_TEST record 3 1 0 0
    sleep 15
    
    # Get latest video file
    VIDEO_FILE=$(ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 2>/dev/null | head -1)

    if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}FAIL: No video file generated${NC}"
        press_any_key
        return
    fi

    echo "Generated file: $VIDEO_FILE"

    # Validate file timestamp (within 5 minutes)
    if ! validate_device_file "$VIDEO_FILE" "$(date +%s)" 300; then
        echo -e "${RED}FAIL: File validation failed${NC}"
        press_any_key
        return
    fi

    # Validate file timestamp (within 5 minutes)
    if ! validate_device_file "$VIDEO_FILE" "$(date +%s)" 300; then
        echo -e "${RED}FAIL: File validation failed${NC}"
        press_any_key
        return
    fi
    
    # Analyze with mp4info
    MP4_OUTPUT=$($MP4INFO "$VIDEO_FILE" 2>&1)
    
    # Check audio track and bitrate
    AUDIO_LINE=$(echo "$MP4_OUTPUT" | grep "2.*audio.*AAC")
    if echo "$AUDIO_LINE" | grep -q "kbps"; then
        BITRATE=$(echo "$AUDIO_LINE" | grep -o '[0-9]* kbps' | grep -o '[0-9]*')
        if [ -n "$BITRATE" ] && [ "$BITRATE" -gt 2 ]; then
            echo -e "${GREEN}PASS: Audio record test passed${NC}"
            echo "Details: $AUDIO_LINE"
            rm -f "$VIDEO_FILE"
            press_any_key
            return
        fi
    fi
    
    echo -e "${RED}FAIL: Audio record test failed${NC}"
    echo "Output: $MP4_OUTPUT"
    press_any_key
}

test_photo_capture() {
    echo -e "\n${YELLOW}=== Photo Capture Test ===${NC}"
    
    check_tool "$RECORD_TEST" || return
    check_tool "$IMG_CHECK" || return
    
    echo "Capturing photo..."
    $RECORD_TEST photo 2
    sleep 2
    
    # Get latest photo file
    PHOTO_FILE=$(ls -t /sdcard/falcon/$(date +%Y%m%d)/*.jpg 2>/dev/null | head -1)

    if [ -z "$PHOTO_FILE" ] || [ ! -f "$PHOTO_FILE" ]; then
        echo -e "${RED}FAIL: No photo file generated${NC}"
        press_any_key
        return
    fi

    echo "Generated file: $PHOTO_FILE"

    # Validate file timestamp (within 1 minute for photos)
    if ! validate_device_file "$PHOTO_FILE" "$(date +%s)" 60; then
        echo -e "${RED}FAIL: File validation failed${NC}"
        press_any_key
        return
    fi
    
    # Analyze with IMG_check.sh
    IMG_OUTPUT=$($IMG_CHECK "$PHOTO_FILE" 2>&1)
    
    if echo "$IMG_OUTPUT" | grep -q "status:normal"; then
        echo -e "${GREEN}PASS: Photo capture test passed${NC}"
        echo "Details: $IMG_OUTPUT"
        rm -f "$PHOTO_FILE"
    else
        echo -e "${RED}FAIL: Photo capture test failed${NC}"
        echo "Output: $IMG_OUTPUT"
    fi
    
    press_any_key
}

test_horizontal_motor() {
    echo -e "\n${YELLOW}=== Horizontal Motor Test ===${NC}"
    
    check_tool "$HORIZONTAL_TEST" || return
    
    echo "Running horizontal motor test..."
    MOTOR_OUTPUT=$($HORIZONTAL_TEST 2>&1)
    
    if echo "$MOTOR_OUTPUT" | grep -q "motor status:normal"; then
        echo -e "${GREEN}PASS: Horizontal motor test passed${NC}"
        echo "Details: $MOTOR_OUTPUT"
    else
        echo -e "${RED}FAIL: Horizontal motor test failed${NC}"
        echo "Output: $MOTOR_OUTPUT"
    fi
    
    press_any_key
}

test_pitch_motor() {
    echo -e "\n${YELLOW}=== Pitch Motor Test ===${NC}"
    
    check_tool "$PITCH_TEST" || return
    
    echo "Running pitch motor test..."
    MOTOR_OUTPUT=$($PITCH_TEST 2>&1)
    
    if echo "$MOTOR_OUTPUT" | grep -q "motor status:normal"; then
        echo -e "${GREEN}PASS: Pitch motor test passed${NC}"
        echo "Details: $MOTOR_OUTPUT"
    else
        echo -e "${RED}FAIL: Pitch motor test failed${NC}"
        echo "Output: $MOTOR_OUTPUT"
    fi
    
    press_any_key
}

test_led_light() {
    echo -e "\n${YELLOW}=== LED Light Test ===${NC}"
    echo -e "${YELLOW}MANUAL TEST: Please observe LED light status${NC}"
    echo "Running LED test commands..."
    
    # Actual LED test command for Falcon/Falcon-Air
    printf '\x01' | mosquitto_pub -h localhost -t BER -s
    
    echo "LED test completed"
    echo -e "${YELLOW}Please confirm visually if LEDs are working correctly${NC}"
    
    press_any_key
}

test_buzzer() {
    echo -e "\n${YELLOW}=== Buzzer Test ===${NC}"
    echo -e "${YELLOW}MANUAL TEST: Please listen for buzzer sound${NC}"
    echo "Running buzzer test commands..."

    # Actual buzzer test command for Falcon/Falcon-Air
    printf '\x02' | mosquitto_pub -h localhost -t "AIR" -s
    sleep 3

    echo "Buzzer test completed"
    echo -e "${YELLOW}Please confirm if you heard the buzzer sound${NC}"

    press_any_key
}

test_sdcard_check() {
    echo -e "\n${YELLOW}=== SD Card Check Test ===${NC}"

    check_tool "$SDCARD_TEST" || return

    echo "Running SD card check..."
    SDCARD_OUTPUT=$($SDCARD_TEST 2>&1)
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}PASS: SD card check passed${NC}"
        echo "Details: $SDCARD_OUTPUT"
    else
        echo -e "${RED}FAIL: SD card check failed${NC}"
        echo "Details: $SDCARD_OUTPUT"
    fi

    press_any_key
}

test_record_mark() {
    echo -e "\n${YELLOW}=== Record Mark Test ===${NC}"

    check_tool "$RECORD_TEST" || return

    echo "Starting record with mark test..."
    $RECORD_TEST record 0 1 0 0
    sleep 5
    $RECORD_TEST mark
    sleep 5
    $RECORD_TEST record 3 1 0 0
    sleep 5

    # Get latest video file
    VIDEO_FILE=$(ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 2>/dev/null | head -1)

    if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}FAIL: No video file generated${NC}"
        press_any_key
        return
    fi

    echo "Generated file: $VIDEO_FILE"

    # Check for mark file
    # 增加额外等待时间，确保文件完全写入
    sleep 3

    # 构造mark文件路径（与Python版本完全一致）
    VIDEO_DIR=$(dirname "$VIDEO_FILE")
    VIDEO_FILENAME=$(basename "$VIDEO_FILE")
    MARK_FILENAME="${VIDEO_FILENAME%.mp4}.mark"
    MARK_PATH="$VIDEO_DIR/.data/$MARK_FILENAME"

    echo "Video file: $VIDEO_FILE"
    echo "Video dir: $VIDEO_DIR"
    echo "Video filename: $VIDEO_FILENAME"
    echo "Mark filename: $MARK_FILENAME"
    echo "Checking mark file: $MARK_PATH"

    # 使用ls -la检查mark文件（与Python版本保持一致）
    if ls -la "$MARK_PATH" >/dev/null 2>&1; then
        echo -e "${GREEN}PASS: Record mark test passed${NC}"
        echo "Mark file found: $MARK_PATH"
    else
        echo -e "${RED}FAIL: Record mark test failed${NC}"
        echo "Mark file not found: $MARK_PATH"
        echo "Expected path: $VIDEO_DIR/.data/$MARK_FILENAME"
    fi

    press_any_key
}

test_mbtn_record() {
    echo -e "\n${YELLOW}=== M-Button Record Test ===${NC}"

    check_tool "$RECORD_TEST" || return
    check_tool "$MP4INFO" || return

    echo "Starting M-button record test (90 seconds)..."
    $RECORD_TEST record 0 2 0 0
    echo "Recording for 90 seconds..."
    sleep 90
    $RECORD_TEST record 3 2 0 0
    sleep 5

    # Get latest video file
    VIDEO_FILE=$(ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 2>/dev/null | head -1)

    if [ -z "$VIDEO_FILE" ] || [ ! -f "$VIDEO_FILE" ]; then
        echo -e "${RED}FAIL: No video file generated${NC}"
        press_any_key
        return
    fi

    echo "Generated file: $VIDEO_FILE"

    # Validate file timestamp (within 2 minutes for M-button record)
    if ! validate_device_file "$VIDEO_FILE" "$(date +%s)" 120; then
        echo -e "${RED}FAIL: File validation failed${NC}"
        press_any_key
        return
    fi

    # Analyze with mp4info
    MP4_OUTPUT=$($MP4INFO "$VIDEO_FILE" 2>&1)

    # Check video and audio tracks
    VIDEO_TRACK=$(echo "$MP4_OUTPUT" | grep "1.*video.*H264")
    AUDIO_TRACK=$(echo "$MP4_OUTPUT" | grep "2.*audio.*AAC")

    if [ -n "$VIDEO_TRACK" ] && [ -n "$AUDIO_TRACK" ]; then
        echo -e "${GREEN}PASS: M-button record test passed${NC}"
        echo "Video: $(echo "$VIDEO_TRACK" | cut -d: -f2-)"
        echo "Audio: $(echo "$AUDIO_TRACK" | cut -d: -f2-)"
    else
        echo -e "${RED}FAIL: M-button record test failed${NC}"
        echo "MP4 Info: $MP4_OUTPUT"
    fi

    press_any_key
}

run_all_tests() {
    echo -e "\n${YELLOW}=== Running All Tests ===${NC}"
    echo "This will run all 10 tests in sequence"
    echo

    test_video_record
    test_audio_record
    test_photo_capture
    test_horizontal_motor
    test_pitch_motor
    test_led_light
    test_buzzer
    test_sdcard_check
    test_record_mark
    test_mbtn_record

    echo -e "\n${GREEN}=== All tests completed ===${NC}"
    press_any_key
}

# =========================================================
# Main Menu
# =========================================================

show_menu() {
    clear
    echo "========================================"
    echo "  RV1126B/RK3576 Automated Test Menu"
    echo "  Platform: $PLATFORM"
    echo "========================================"
    echo "  0. Run All Tests"
    echo "  1. Video Record Test"
    echo "  2. Audio Record Test"
    echo "  3. Photo Capture Test"
    echo "  4. Horizontal Motor Test"
    echo "  5. Pitch Motor Test"
    echo "  6. LED Light Test (Manual)"
    echo "  7. Buzzer Test (Manual)"
    echo "  8. SD Card Check Test"
    echo "  9. Record Mark Test"
    echo " 10. M-Button Record Test"
    echo " 11. Exit"
    echo "========================================"
}

# =========================================================
# Main loop
# =========================================================

main() {
    while true; do
        show_menu
        
        read -p "Enter selection [0-11]: " choice
        case $choice in
            0) run_all_tests ;;
            1) test_video_record ;;
            2) test_audio_record ;;
            3) test_photo_capture ;;
            4) test_horizontal_motor ;;
            5) test_pitch_motor ;;
            6) test_led_light ;;
            7) test_buzzer ;;
            8) test_sdcard_check ;;
            9) test_record_mark ;;
            10) test_mbtn_record ;;
            11)
                echo "Exiting..."
                echo
                echo "Required external tools to upload to /tmp/:"
                echo "  record_test"
                echo "  mp4info_rk3576  (Falcon)"
                echo "  mp4info_rv1126b (Falcon-Air)"
                echo
                echo "All other helper scripts are embedded and auto-generated."
                echo
                echo "Upload command example:"
                echo "  scp tools/record_tool/record_test root@<device-ip>:/tmp/"
                echo "  scp tools/mp4info/* root@<device-ip>:/tmp/"
                echo "  chmod +x /tmp/*"
                exit 0
                ;;
            *)
                echo "Invalid selection, please try again"
                sleep 1
                ;;
        esac
    done
}

# Run main
main
