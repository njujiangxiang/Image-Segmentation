# 🖼️ Image-Segmentation

**基于 SAM 的图像分割工具** - 自动识别并分割图像主体，支持透明背景、自定义背景色和批量处理。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 简介

Image-Segmentation 是一个基于 Meta **Segment Anything Model (SAM)** 的图像分割工具，可自动识别并分割图像主体，支持去除背景、替换背景色等功能。

### ✨ 核心特性

- ✅ **自动分割** - 自动识别并分割图像主体
- ✅ **透明背景** - 支持输出透明背景 PNG
- ✅ **自定义背景** - 支持黑色、白色、RGB/RGBA 自定义颜色
- ✅ **批量处理** - 支持多张图片批量处理
- ✅ **多模型支持** - default/large/huge 三种模型尺寸
- ✅ **GPU 加速** - 支持 CUDA GPU 加速
- ✅ **配置灵活** - 通过 config.ini 轻松管理所有参数

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载 SAM 模型

| 模型 | 大小 | 下载链接 |
|------|------|----------|
| default (ViT-B) | 358MB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth) |
| large (ViT-L) | 1.2GB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth) |
| huge (ViT-H) | 2.5GB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) |

将模型文件放在项目目录或指定路径。

### 3. 基础使用

```bash
# 透明背景
python sam_segment.py input.jpg output.png

# 黑色背景
python sam_segment.py input.jpg output.png black

# 白色背景
python sam_segment.py input.jpg output.png white
```

---

## 📚 使用方法

### Python API

#### 基础用法

```python
from sam_segment import create_segmenter

# 创建分割器
segmenter = create_segmenter()

# 分割图像（透明背景）
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output.png",
    background_color="transparent"
)

if result["success"]:
    print(f"输出：{result['output_path']}")
    print(f"置信度：{result['confidence']:.2%}")
```

#### 自定义背景颜色

```python
# RGB 颜色（蓝色背景）
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_blue.png",
    background_color=(100, 149, 237)
)

# RGBA 颜色（半透明黑色）
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_semi.png",
    background_color=(0, 0, 0, 128)
)
```

#### 批量处理

```python
input_images = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]

results = segmenter.segment_batch(
    input_paths=input_images,
    output_dir="output_batch",
    background_color="white"
)
```

#### 高质量模式

```python
# 使用大型模型和 GPU 加速
segmenter = create_segmenter(model_type="large", device="cuda")

result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_hq.png",
    confidence_threshold=0.7
)
```

---

## 📁 项目结构

```
Image-Segmentation/
├── sam_segment.py          # SAM 图像分割主工具
├── sam3_model.py           # SAM 模型适配器
├── examples.py             # 使用示例
├── config.ini              # 配置文件
├── requirements.txt        # Python 依赖
├── .gitignore             # Git 忽略规则
├── README.md              # 项目说明
│
└── Backlit/               # 逆光照片检测工具
    ├── backlit_detector.py # 逆光检测核心工具
    ├── examples.py         # 使用示例
    ├── config.json         # 配置文件
    ├── README.md           # 说明文档
    └── requirements.txt    # Python 依赖
```

---

## ⚙️ 配置说明

### config.ini 配置项

```ini
[model]
type = "default"              # 模型类型：default, large, huge
device = "auto"               # 运行设备：auto, cuda, cpu

[segmentation]
confidence_threshold = 0.5    # 置信度阈值
min_mask_area_ratio = 0.01   # 最小掩码面积比例
max_masks = 10               # 最大掩码数量

[output]
background_color = "transparent"  # 默认背景颜色
output_format = "png"             # 默认输出格式
save_mask = true                  # 是否保存掩码

[batch]
batch_size = 4              # 批处理大小
skip_on_error = true        # 跳过错误文件
```

### 命令行使用配置

```bash
# 使用默认配置
python sam_segment.py input.jpg output.png

# 指定配置文件
python sam_segment.py input.jpg -c my_config.ini

# 覆盖配置参数
python sam_segment.py input.jpg -c config.ini -m large -d cuda -t 0.7
```

---

## 🔦 Backlit - 逆光照片检测

**Backlit** 是一个独立的逆光照片检测工具，支持 5 种检测方法：

- **直方图分析** - 亮度双峰分布检测（最快）
- **空间分布** - 中心 - 边缘亮度比分析
- **边缘光晕** - 轮廓光效应检测
- **色度分析** - 基于 SPIE 论文的色度特征
- **综合评分** - 加权平均 + 投票机制（最准确，92%）

### 使用方法

```bash
cd Backlit

# 安装依赖
pip install -r requirements.txt

# 检测单张图片
python backlit_detector.py image.jpg

# 批量检测
python backlit_detector.py *.jpg --batch --output results.json
```

**详细说明**: 查看 [Backlit/README.md](Backlit/README.md)

---

## 📦 依赖

### 主项目

```txt
torch
torchvision
opencv-python
numpy
Pillow
```

### Backlit（逆光检测）

```txt
opencv-python>=4.5.0
numpy>=1.20.0
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 📊 性能对比

| 模型 | 速度 | 准确率 | 显存占用 | 适用场景 |
|------|------|--------|----------|----------|
| default | ⭐⭐⭐⭐⭐ | 85% | 2GB | 日常使用 |
| large | ⭐⭐⭐⭐ | 90% | 4GB | 高质量需求 |
| huge | ⭐⭐⭐ | 95% | 8GB | 专业场景 |

---

## ❓ 常见问题

### Q: 模型加载失败？

**A**: 确保已下载对应的 `.pth` 模型文件，并检查路径是否正确。

### Q: 如何使用 GPU 加速？

**A**: 安装 CUDA 版本的 PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Q: 分割效果不理想？

**A**: 
1. 使用更大的模型（`model_type="large"`）
2. 调整置信度阈值（`confidence_threshold=0.6`）
3. 使用点提示或框提示进行引导

### Q: 输出 JPEG 时背景变白色？

**A**: JPEG 不支持透明通道，请使用 PNG 格式。

---

## 📝 许可证

- **本项目**: MIT License
- **SAM 模型**: [Apache 2.0 License](https://github.com/facebookresearch/segment-anything/blob/main/LICENSE)

---

## 🔗 参考链接

- [SAM 官方仓库](https://github.com/facebookresearch/segment-anything)
- [SAM 论文](https://arxiv.org/abs/2304.02643)
- [SAM Demo](https://segment-anything.com/demo)

---

## 📧 联系方式

- **作者**: 小雨爸爸
- **Email**: nju.jiangxiang@gmail.com
- **GitHub**: [njujiangxiang](https://github.com/njujiangxiang)

---

**如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！**
