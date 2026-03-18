# 逆光图像处理器 (Backlight Image Processor)

用于处理逆光拍摄的图片，通过多种算法增强图像亮度和对比度，使暗部细节更清晰，同时保持高光区域不过曝。

## 功能特点

- **多种处理算法**：支持 Gamma 校正、CLAHE、阴影增强、HDR 风格等多种算法
- **灵活的参数配置**：支持配置文件和命令行参数两种方式
- **批量处理**：支持单张处理和批量处理两种模式
- **自适应混合**：根据像素亮度自适应调整处理强度
- **完整的代码注释**：每个函数都有详细的中文注释

## 环境要求

- Python 3.7+
- OpenCV-Python
- NumPy

## 安装依赖

```bash
pip install opencv-python numpy
```

## 使用方法

### 1. 处理单张图片

```bash
# 基本用法（使用默认参数）
python backlight_processor.py input.jpg output.jpg

# 使用配置文件
python backlight_processor.py input.jpg output.jpg --config config.json

# 使用命令行参数
python backlight_processor.py input.jpg output.jpg --gamma 2.0 --brightness 1.5

# 指定处理方法
python backlight_processor.py input.jpg output.jpg --method blend
```

### 2. 批量处理图片目录

```bash
# 批量处理整个目录
python backlight_processor.py ./input_images/ ./output_images/ --batch

# 批量处理并使用自定义参数
python backlight_processor.py ./input_images/ ./output_images/ --batch --gamma 1.8

# 批量处理并覆盖已存在的文件
python backlight_processor.py ./input_images/ ./output_images/ --batch --overwrite
```

### 3. 生成默认配置文件

```bash
# 生成默认配置文件
python backlight_processor.py dummy dummy --generate-config config.json
```

### 4. 运行示例代码

```bash
# 运行示例代码（会自动创建测试图片并处理）
python examples.py
```

## 命令行参数说明

### 基本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入图片路径或输入目录 | 必填 |
| `output` | 输出图片路径或输出目录 | 必填 |
| `--batch` | 批量处理模式 | 关闭 |
| `--config` | 配置文件路径 (JSON) | 无 |
| `--method` | 处理方法 | `all` |
| `--overwrite` | 覆盖已存在的文件 | 关闭 |

### 图像参数

| 参数 | 说明 | 默认值 | 取值范围 |
|------|------|--------|----------|
| `--gamma` | Gamma 校正值 | 1.5 | 0.5-3.0 |
| `--clip-limit` | CLAHE 对比度限制 | 2.0 | 1.0-10.0 |
| `--tile-grid` | CLAHE 网格大小 | 8 | 4-16 |
| `--blur-kernel` | 模糊核大小 | 51 | 11-101 (奇数) |
| `--brightness` | 亮度增强系数 | 1.2 | 0.5-3.0 |
| `--shadow-threshold` | 阴影阈值 | 0.3 | 0.1-0.5 |
| `--highlight-threshold` | 高光阈值 | 0.8 | 0.6-0.95 |
| `--hdr-strength` | HDR 强度 | 0.7 | 0.0-1.0 |

## 处理方法说明

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| `gamma` | Gamma 校正，整体提亮图像 | 整体偏暗的图片 |
| `clahe` | 自适应直方图均衡化，增强局部对比度 | 对比度不足的图片 |
| `shadow` | 阴影增强，选择性提亮暗部 | 前景太暗的逆光图片 |
| `hdr` | HDR 风格，多尺度融合 | 大光比场景 |
| `blend` | 自适应混合（推荐） | 大多数逆光场景 |
| `all` | 完整处理流程 | 严重逆光的图片 |

## 配置参数说明

```json
{
    "gamma": 1.5,
    "clip_limit": 2.0,
    "tile_grid_size": 8,
    "blur_kernel_size": 51,
    "brightness_factor": 1.2,
    "shadow_threshold": 0.3,
    "highlight_threshold": 0.8,
    "hdr_strength": 0.7
}
```

### 参数详解

- **gamma**: Gamma 校正值。值越大图像越亮，建议范围 1.2-2.0
- **clip_limit**: CLAHE 对比度限制。值越大对比度越强，但可能产生噪点
- **tile_grid_size**: CLAHE 网格大小。值越小局部增强越明显
- **blur_kernel_size**: 模糊核大小。用于阴影检测，必须是奇数
- **brightness_factor**: 亮度增强系数。控制阴影提亮的强度
- **shadow_threshold**: 阴影阈值。低于此值的区域被认为是阴影
- **highlight_threshold**: 高光阈值。高于此值的区域被认为是高光
- **hdr_strength**: HDR 强度。0 为原图，1 为最强 HDR 效果

## 使用示例

### 示例 1: 处理轻度逆光图片

```bash
python backlight_processor.py photo.jpg output.jpg --gamma 1.3 --method blend
```

### 示例 2: 处理严重逆光图片

```bash
python backlight_processor.py dark_photo.jpg output.jpg --gamma 2.0 --brightness 1.5 --method all
```

### 示例 3: 批量处理旅游照片

```bash
python backlight_processor.py ./vacation/ ./vacation_enhanced/ --batch --config config.json
```

### 示例 4: 创建温和的 HDR 效果

```bash
python backlight_processor.py landscape.jpg output.jpg --method hdr --hdr-strength 0.4
```

## Python 代码调用示例

```python
import cv2
from backlight_processor import BacklightProcessor

# 方法 1: 使用默认配置
processor = BacklightProcessor()
image = cv2.imread("input.jpg")
result = processor.process(image)
cv2.imwrite("output.jpg", result)

# 方法 2: 使用自定义配置
config = {
    "gamma": 1.8,
    "clip_limit": 3.0,
    "brightness_factor": 1.5,
}
processor = BacklightProcessor(config=config)
result = processor.process(image, method="blend")

# 方法 3: 从配置文件加载
from backlight_processor import load_config
config = load_config("config.json")
processor = BacklightProcessor(config=config)

# 方法 4: 批量处理
stats = processor.process_batch(
    input_dir="./input/",
    output_dir="./output/",
    method="all",
    overwrite=True
)
```

## 支持的图片格式

- JPEG / JPG
- PNG
- BMP
- TIFF / TIF
- WebP

## 注意事项

1. **模糊核大小**必须是奇数，如果输入偶数会自动加 1
2. **批量处理**时，输出目录不存在会自动创建
3. **覆盖模式**需要显式使用 `--overwrite` 参数，否则已存在的文件会被跳过
4. 处理**大尺寸图片**时可能需要较多内存和处理时间
5. 建议先对单张图片测试参数，确认效果后再批量处理

## 文件结构

```
Backlight/
├── backlight_processor.py   # 主程序（含详细注释）
├── examples.py              # 调用示例代码
├── config.json              # 配置文件
└── README.md                # 使用说明
```

## 许可证

MIT License
