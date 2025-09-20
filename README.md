# 图片水印添加工具

一个基于Python的命令行工具，用于从图片的EXIF信息中提取拍摄时间，并将其作为水印添加到图片上。

## 功能特性

- 📸 自动读取图片EXIF信息中的拍摄时间
- 🎨 支持自定义水印字体大小、颜色和位置
- 📁 批量处理目录中的所有图片
- 🔍 详细的EXIF信息输出，便于调试
- 💾 自动创建输出目录保存带水印的图片

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python image_watermark.py <图片目录路径>
```

### 高级选项

```bash
python image_watermark.py <图片目录路径> [选项]
```

#### 可用选项：

- `--font-size SIZE`: 设置字体大小（默认：24）
- `--color COLOR`: 设置水印颜色（可选：white, black, red, blue 或十六进制颜色如 #FF0000，默认：white）
- `--position POSITION`: 设置水印位置（可选：top-left, top-right, bottom-left, bottom-right, center，默认：bottom-right）

### 使用示例

1. **基本使用**：
   ```bash
   python image_watermark.py ./photos
   ```

2. **自定义字体大小和颜色**：
   ```bash
   python image_watermark.py ./photos --font-size 32 --color red
   ```

3. **使用十六进制颜色**：
   ```bash
   python image_watermark.py ./photos --color "#FF5733"
   ```

4. **设置水印位置为左上角**：
   ```bash
   python image_watermark.py ./photos --position top-left --color black
   ```

5. **居中显示水印**：
   ```bash
   python image_watermark.py ./photos --position center --font-size 28
   ```

## 输出说明

- 程序会在原目录下创建一个名为 `原目录名_watermark` 的子目录
- 处理后的图片会以 `watermarked_` 前缀保存
- 程序会输出详细的EXIF信息，包括：
  - 拍摄时间相关字段
  - 相机信息（品牌、型号）
  - 拍摄参数（光圈、快门、ISO等）

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)

## 注意事项

1. 确保图片文件包含EXIF信息，否则无法提取拍摄时间
2. 如果系统没有arial字体，程序会尝试使用系统默认字体
3. 输出图片会保持原图的质量设置
4. 程序会自动跳过无法处理的文件并继续处理其他文件

## 错误处理

程序具有完善的错误处理机制：
- 自动跳过没有EXIF信息的图片
- 处理文件读取错误
- 处理字体加载失败的情况
- 提供详细的错误信息

## 技术实现

- 使用 `Pillow` 库进行图片处理和水印绘制
- 使用 `Pillow` 内置EXIF功能读取图片元数据
- 支持多种时间字段的自动识别
- 智能字体回退机制
