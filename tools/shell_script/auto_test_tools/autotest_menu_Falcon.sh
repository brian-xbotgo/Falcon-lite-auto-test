#!/bin/bash
# =========================================================
# RV1126B/RK3576 Automated Test Menu
# All automated test cases integrated - SELF CONTAINED
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
    
    # Make all scripts executable
    chmod +x "$IMG_CHECK" "$HORIZONTAL_TEST" "$PITCH_TEST"
}

# Cleanup function
cleanup() {
    rm -f "$IMG_CHECK" "$HORIZONTAL_TEST" "$PITCH_TEST"
    echo -e "\nCleaned up temporary scripts"
}

# Generate helper scripts on startup
generate_helper_scripts

# Register cleanup trap
trap cleanup EXIT

##设备判断暂时备注 后续需要修复
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

MP4INFO="/tmp/mp4info_rk3576"
PLATFORM="Falcon"

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
        echo -e "${RED}FAIL: No audio file generated${NC}"
        press_any_key
        return
    fi
    
    echo "Generated file: $VIDEO_FILE"
    
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
    printf '\xFE' | mosquitto_pub -h localhost -t CGA -s
    sleep 3
    
    echo "Buzzer test completed"
    echo -e "${YELLOW}Please confirm if you heard the buzzer sound${NC}"
    
    press_any_key
}

run_all_tests() {
    echo -e "\n${YELLOW}=== Running All Tests ===${NC}"
    echo "This will run all 7 tests in sequence"
    echo
    
    test_video_record
    test_audio_record
    test_photo_capture
    test_horizontal_motor
    test_pitch_motor
    test_led_light
    test_buzzer
    
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
    echo "  8. Exit"
    echo "========================================"
}

# =========================================================
# Main loop
# =========================================================

main() {
    while true; do
        show_menu
        
        read -p "Enter selection [0-8]: " choice
        case $choice in
            0) run_all_tests ;;
            1) test_video_record ;;
            2) test_audio_record ;;
            3) test_photo_capture ;;
            4) test_horizontal_motor ;;
            5) test_pitch_motor ;;
            6) test_led_light ;;
            7) test_buzzer ;;
            8) 
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
