# -*- coding: utf-8 -*-
"""
FFMPEG服务模块
功能：媒体文件信息查询、格式转换等
作者：系统自动生成
创建时间：2026-04-21
"""
import os
import json
import subprocess
from typing import Tuple
from .log_service import log
from .config import TOOLS_DIR


class FFMPEGService:
    """
    FFMPEG封装服务
    使用项目自带的静态二进制文件，不需要系统安装FFMPEG
    """
    
    # FFMPEG工具路径
    FFMPEG_PATH = os.path.join(TOOLS_DIR, "ffmpeg", "ffmpeg.exe")
    FFPROBE_PATH = os.path.join(TOOLS_DIR, "ffmpeg", "ffprobe.exe")
    
    @staticmethod
    def _run_ffprobe(args: list) -> Tuple[bool, str]:
        """内部执行ffprobe命令"""
        if not os.path.exists(FFMPEGService.FFPROBE_PATH):
            return False, "ffprobe工具不存在"
            
        cmd = [FFMPEGService.FFPROBE_PATH] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, f"执行异常: {str(e)}"
    
    @staticmethod
    def get_mp4_info(file_path: str) -> Tuple[bool, int, int, float]:
        """
        获取MP4文件信息
        :param file_path: MP4文件路径
        :return: (是否成功, 宽度, 高度, 帧率)
        """
        if not os.path.exists(file_path):
            return False, 0, 0, 0.0
            
        log.debug(f"获取MP4信息: {file_path}")
        
        # 以JSON格式输出流信息
        args = [
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "v:0",
            file_path
        ]
        
        success, output = FFMPEGService._run_ffprobe(args)
        if not success:
            log.error(f"获取MP4信息失败: {output}")
            return False, 0, 0, 0.0
            
        try:
            data = json.loads(output)
            if "streams" not in data or len(data["streams"]) == 0:
                return False, 0, 0, 0.0
                
            stream = data["streams"][0]
            width = stream.get("width", 0)
            height = stream.get("height", 0)
            
            # 解析帧率
            r_frame_rate = stream.get("r_frame_rate", "0/1")
            if "/" in r_frame_rate:
                num, den = map(int, r_frame_rate.split("/", 1))
                fps = num / den if den != 0 else 0.0
            else:
                fps = float(r_frame_rate)
                
            log.debug(f"MP4信息: {width}x{height}, {fps:.2f} fps")
            return True, width, height, round(fps, 2)
            
        except Exception as e:
            log.error(f"解析MP4信息失败: {str(e)}")
            return False, 0, 0, 0.0
    
    @staticmethod
    def get_image_info(file_path: str) -> Tuple[bool, int, int]:
        """
        获取图片文件信息
        :param file_path: 图片文件路径（支持JPG/PNG/BMP等）
        :return: (是否成功, 宽度, 高度)
        """
        if not os.path.exists(file_path):
            return False, 0, 0
            
        log.debug(f"获取图片信息: {file_path}")
        
        # 以JSON格式输出流信息
        args = [
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            file_path
        ]
        
        success, output = FFMPEGService._run_ffprobe(args)
        if not success:
            log.error(f"获取图片信息失败: {output}")
            return False, 0, 0
            
        try:
            data = json.loads(output)
            if "streams" not in data or len(data["streams"]) == 0:
                return False, 0, 0
                
            stream = data["streams"][0]
            width = stream.get("width", 0)
            height = stream.get("height", 0)
            
            log.debug(f"图片信息: {width}x{height}")
            return True, width, height
            
        except Exception as e:
            log.error(f"解析图片信息失败: {str(e)}")
            return False, 0, 0
