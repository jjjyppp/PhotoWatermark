#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印添加工具
从EXIF信息中提取拍摄时间作为水印，添加到图片上
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
from datetime import datetime


class ImageWatermarker:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        
    def get_exif_data(self, image_path):
        """读取图片的EXIF信息"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data is not None:
                    exif = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = value
                    return exif
                return None
        except Exception as e:
            print(f"读取EXIF信息失败 {image_path}: {e}")
            return None
    
    def extract_datetime(self, exif_data):
        """从EXIF数据中提取拍摄时间"""
        if not exif_data:
            return None
            
        # 尝试不同的时间字段
        time_fields = [
            'DateTimeOriginal',
            'DateTime',
            'DateTimeDigitized'
        ]
        
        for field in time_fields:
            if field in exif_data:
                try:
                    time_str = str(exif_data[field])
                    # 解析时间字符串
                    dt = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return None
    
    def print_exif_info(self, image_path, exif_data):
        """打印EXIF信息用于调试"""
        print(f"\n=== {os.path.basename(image_path)} EXIF信息 ===")
        if not exif_data:
            print("无EXIF信息")
            return
            
        # 打印相关的时间字段
        time_fields = [
            'DateTimeOriginal',
            'DateTime', 
            'DateTimeDigitized'
        ]
        
        for field in time_fields:
            if field in exif_data:
                print(f"{field}: {exif_data[field]}")
        
        # 打印其他有用的信息
        info_fields = [
            'Make',
            'Model',
            'FNumber',
            'ExposureTime',
            'ISOSpeedRatings'
        ]
        
        for field in info_fields:
            if field in exif_data:
                print(f"{field}: {exif_data[field]}")
    
    def get_watermark_position(self, img_width, img_height, position, text_width, text_height, margin=20):
        """计算水印位置"""
        if position == 'top-left':
            return (margin, margin)
        elif position == 'top-right':
            return (img_width - text_width - margin, margin)
        elif position == 'bottom-left':
            return (margin, img_height - text_height - margin)
        elif position == 'bottom-right':
            return (img_width - text_width - margin, img_height - text_height - margin)
        elif position == 'center':
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        else:
            return (margin, margin)  # 默认左上角
    
    def add_watermark(self, image_path, output_path, text, font_size=24, color='white', position='bottom-right'):
        """给图片添加水印"""
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 创建透明图层用于绘制水印
                watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark)
                
                # 尝试加载字体，如果失败则使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算水印位置
                x, y = self.get_watermark_position(
                    img.width, img.height, position, text_width, text_height
                )
                
                # 解析颜色
                if color == 'white':
                    text_color = (255, 255, 255, 255)
                elif color == 'black':
                    text_color = (0, 0, 0, 255)
                elif color == 'red':
                    text_color = (255, 0, 0, 255)
                elif color == 'blue':
                    text_color = (0, 0, 255, 255)
                elif color.startswith('#'):
                    # 解析十六进制颜色
                    try:
                        hex_color = color.lstrip('#')
                        if len(hex_color) == 6:
                            r = int(hex_color[0:2], 16)
                            g = int(hex_color[2:4], 16)
                            b = int(hex_color[4:6], 16)
                            text_color = (r, g, b, 255)
                        else:
                            text_color = (255, 255, 255, 255)  # 默认白色
                    except ValueError:
                        text_color = (255, 255, 255, 255)  # 默认白色
                else:
                    text_color = (255, 255, 255, 255)  # 默认白色
                
                # 绘制文本
                draw.text((x, y), text, font=font, fill=text_color)
                
                # 合并原图和水印
                watermarked = Image.alpha_composite(img, watermark)
                
                # 转换回RGB模式并保存
                if watermarked.mode == 'RGBA':
                    watermarked = watermarked.convert('RGB')
                
                watermarked.save(output_path, quality=95)
                return True
                
        except Exception as e:
            print(f"添加水印失败 {image_path}: {e}")
            return False
    
    def process_directory(self, input_dir, font_size=24, color='white', position='bottom-right'):
        """处理目录中的所有图片"""
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"错误：目录不存在 {input_dir}")
            return
        
        # 创建输出目录（作为原目录的子目录）
        output_dir = input_path / f"{input_path.name}_watermark"
        output_dir.mkdir(exist_ok=True)
        print(f"输出目录：{output_dir}")
        
        # 获取所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        # 去重，避免同一文件被处理两次
        image_files = list(set(image_files))
        
        if not image_files:
            print(f"在目录 {input_dir} 中未找到支持的图片文件")
            return
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        # 处理每个图片文件
        for image_file in image_files:
            print(f"\n处理文件：{image_file.name}")
            
            # 读取EXIF信息
            exif_data = self.get_exif_data(image_file)
            self.print_exif_info(image_file, exif_data)
            
            # 提取拍摄时间
            datetime_str = self.extract_datetime(exif_data)
            if not datetime_str:
                print("未找到拍摄时间信息，跳过此文件")
                continue
            
            print(f"提取的拍摄时间：{datetime_str}")
            
            # 添加水印
            output_file = output_dir / f"watermarked_{image_file.name}"
            if self.add_watermark(image_file, output_file, datetime_str, font_size, color, position):
                print(f"✓ 水印添加成功：{output_file}")
            else:
                print(f"✗ 水印添加失败：{image_file.name}")


def main():
    parser = argparse.ArgumentParser(description='图片水印添加工具 - 从EXIF信息提取拍摄时间作为水印')
    parser.add_argument('input_dir', help='输入图片目录路径')
    parser.add_argument('--font-size', type=int, default=24, help='字体大小 (默认: 24)')
    parser.add_argument('--color', default='white', 
                       help='水印颜色，支持预定义颜色(white,black,red,blue)或十六进制颜色(如#FF0000) (默认: white)')
    parser.add_argument('--position', 
                       choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                       default='bottom-right', 
                       help='水印位置 (默认: bottom-right)')
    
    args = parser.parse_args()
    
    print("=== 图片水印添加工具 ===")
    print(f"输入目录：{args.input_dir}")
    print(f"字体大小：{args.font_size}")
    print(f"水印颜色：{args.color}")
    print(f"水印位置：{args.position}")
    
    watermarker = ImageWatermarker()
    watermarker.process_directory(args.input_dir, args.font_size, args.color, args.position)
    
    print("\n处理完成！")


if __name__ == "__main__":
    main()

