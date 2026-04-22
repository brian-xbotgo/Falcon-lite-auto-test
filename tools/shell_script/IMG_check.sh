#!/bin/bash

# =========================================================
# 通用工具函数(兼容所有Linux/BusyBox)
# =========================================================
get_file_size() {
    # 使用 wc -c 获取文件大小，最通用的方法
    wc -c < "$1" 2>/dev/null || echo 0
}

read_hex() {
    local file="$1"
    local offset="$2"
    local count="$3"
    # 使用 dd + xxd 读取
    dd if="$file" bs=1 skip="$offset" count="$count" 2>/dev/null | xxd -p 2>/dev/null | tr -d '\n'
}

# =========================================================
# PNG 解析
# =========================================================
get_png_resolution() {
    local file="$1"
    local header=$(read_hex "$file" 16 8)
    if [ -z "$header" ] || [ ${#header} -ne 16 ]; then return 1; fi
    local width=$((16#${header:0:8}))
    local height=$((16#${header:8:8}))
    echo "${width}x${height}"
    return 0
}

check_png() {
    local file="$1"
    local file_size=$(get_file_size "$file")
    
    if [ -z "$file_size" ] || [ "$file_size" -lt 20 ]; then
        echo "status:corruption(The file is too small or empty.)"
        return 1
    fi

    local magic=$(read_hex "$file" 0 8)
    if [ "$magic" != "89504e470d0a1a0a" ]; then
        echo "status:corruption(Invalid PNG file header)"
        return 1
    fi

    local offset=8
    local found_iend=0
    local has_ihdr=0

    while [ $offset -lt $file_size ]; do
        if [ $((offset + 8)) -gt $file_size ]; then break; fi

        local len_hex=$(read_hex "$file" $offset 4)
        [ -z "$len_hex" ] && break
        
        # 兼容 BusyBox 的十六进制转换
        local chunk_len=$(printf "%d" "0x$len_hex" 2>/dev/null || echo 0)
        
        local type_hex=$(read_hex "$file" $((offset + 4)) 4)
        local chunk_type=$(echo "$type_hex" | xxd -p -r 2>/dev/null)
        local total_chunk_size=$((4 + 4 + chunk_len + 4))

        if [ "$chunk_type" = "IHDR" ]; then has_ihdr=1; fi
        if [ "$chunk_type" = "IEND" ]; then found_iend=1; break; fi
        
        offset=$((offset + total_chunk_size))
    done

    if [ $has_ihdr -ne 1 ] || [ $found_iend -ne 1 ]; then
        echo "status:corruption(The file structure is incomplete.)"
        return 1
    fi

    local resolution=$(get_png_resolution "$file")
    if [ $? -eq 0 ]; then
        echo "status:normal"
        echo "resolution:$resolution"
        return 0
    else
        echo "status:corruption(Unable to parse the resolution)"
        return 1
    fi
}

# =========================================================
# JPG 解析(极简稳定版)
# =========================================================
get_jpg_resolution() {
    local file="$1"
    local offset=2
    local file_size=$(get_file_size "$file")

    while [ $offset -lt $file_size ]; do
        local marker=$(read_hex "$file" $offset 2)
        [ -z "$marker" ] && break

        # 找到 SOF0 (Baseline) 或 SOF2 (Progressive)
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

        # 跳过 Marker
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

    # 1. 基础检查
    if [ -z "$file_size" ] || [ "$file_size" -lt 100 ]; then
        echo "status:corruption(The file is too small.)"
        return 1
    fi

    # 2. 检查 SOI 头 (FF D8)
    local head=$(read_hex "$file" 0 2)
    if [ "$head" != "ffd8" ]; then
        echo "status:corruption(Invalid JPG file header)"
        return 1
    fi

    # 3. 尝试解析resolution(能解析出来就是好图)
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

# =========================================================
# 主程序入口
# =========================================================
check_image() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "error:file does not exist"
        return 1
    fi

    local magic=$(read_hex "$file" 0 8)
    
    case "$magic" in
        89504e47*)
            echo "format:PNG"
            check_png "$file"
            ;;
        ffd8*)
            echo "format:JPG"
            check_jpg "$file"
            ;;
        *)
            echo "error:Unsupported format"
            return 1
            ;;
    esac
}

# 执行
if [ $# -eq 1 ]; then
    check_image "$1"
else
    echo "用法:$0 <图片路径>"
fi