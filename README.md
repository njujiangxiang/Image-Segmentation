# SAM 图像分割工具

基于 Meta 的 **Segment Anything Model (SAM)** 实现的图像分割工具，可自动识别并分割图像主体，去除或替换背景。

## 功能特性

- ✅ 自动识别并分割图像主体
- ✅ 去除背景，支持透明背景
- ✅ 自定义背景颜色填充（黑色、白色、RGB/RGBA）
- ✅ 支持批量处理
- ✅ 输出分割掩码
- ✅ 支持多种模型尺寸（default/large/huge）
- ✅ 支持 GPU 加速
- ✅ **配置文件支持** - 通过 config.ini 轻松管理所有参数

## 安装

### 1. 克隆或下载项目

```bash
cd "Image segmentation"
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 下载 SAM 模型

从以下地址下载模型文件（选择其一）：

| 模型类型 | 文件大小 | 下载链接 |
|---------|---------|---------|
| default (ViT-B) | 358MB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth) |
| large (ViT-L) | 1.2GB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth) |
| huge (ViT-H) | 2.5GB | [下载](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) |

将下载的模型文件放在项目目录或指定路径。

## 快速开始

### 命令行使用

```bash
# 基础用法 - 透明背景
python sam_segment.py input.jpg output.png

# 黑色背景
python sam_segment.py input.jpg output.png black

# 白色背景
python sam_segment.py input.jpg output.png white
```

### Python 代码使用

#### 示例 1: 基础用法（透明背景）

```python
from sam_segment import create_segmenter

# 创建分割器
segmenter = create_segmenter()

# 分割图像，去除背景
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_transparent.png",
    background_color="transparent"
)

if result["success"]:
    print(f"输出：{result['output_path']}")
    print(f"置信度：{result['confidence']:.2%}")
```

#### 示例 2: 黑色背景

```python
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_black.png",
    background_color="black"
)
```

#### 示例 3: 自定义背景颜色

```python
# RGB 颜色 (蓝色背景)
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_blue.png",
    background_color=(100, 149, 237)
)

# RGBA 颜色 (半透明黑色)
result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_semi.png",
    background_color=(0, 0, 0, 128)
)
```

#### 示例 4: 高质量模式

```python
# 使用大型模型和 GPU 加速
segmenter = create_segmenter(model_type="large", device="cuda")

result = segmenter.segment(
    input_path="input.jpg",
    output_path="output_hq.png",
    confidence_threshold=0.7  # 更高置信度阈值
)
```

#### 示例 5: 批量处理

```python
input_images = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]

results = segmenter.segment_batch(
    input_paths=input_images,
    output_dir="output_batch",
    background_color="white"
)

for result in results:
    if result["success"]:
        print(f"成功：{result['output_path']}")
```

#### 示例 6: 获取分割掩码

```python
# 获取所有分割掩码
masks = segmenter.get_masks("input.jpg", return_all=True)

print(f"找到 {len(masks)} 个分割区域")
for i, mask in enumerate(masks):
    print(f"区域 {i+1}: 置信度 = {mask['confidence']:.2%}")
```

## API 参考

### SAMImageSegmenter

主分割器类。

#### 初始化

```python
segmenter = SAMImageSegmenter(
    model_type="default",  # 'default', 'large', 'huge'
    device="auto"          # 'auto', 'cuda', 'cpu'
)
```

#### 方法

| 方法 | 说明 |
|-----|------|
| `segment(input_path, output_path, background_color, ...)` | 分割图像并保存 |
| `get_masks(input_path, return_all)` | 获取分割掩码 |
| `segment_batch(input_paths, output_dir, ...)` | 批量处理 |

### segment() 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `input_path` | str | - | 输入图片路径 |
| `output_path` | str | - | 输出图片路径 |
| `background_color` | str/tuple | "transparent" | 背景颜色 |
| `output_format` | str | "png" | 输出格式 |
| `confidence_threshold` | float | 0.5 | 置信度阈值 |

### background_color 可选值

| 值 | 效果 |
|---|------|
| `"transparent"` | 透明背景 |
| `"black"` | 黑色背景 |
| `"white"` | 白色背景 |
| `(R, G, B)` | 自定义 RGB 颜色 |
| `(R, G, B, A)` | 自定义 RGBA 颜色 |

## 运行示例

```bash
# 运行示例 1: 基础用法
python examples.py --example 1 --input test.jpg --output result.png

# 运行示例 2: 黑色背景
python examples.py --example 2 --input test.jpg --output result.png

# 运行示例 3: 自定义颜色
python examples.py --example 3 --input test.jpg --output result.png
```

查看所有示例：

```bash
python examples.py --help
```

## 项目结构

```
Image segmentation/
├── sam_segment.py      # 主分割工具
├── sam3_model.py       # SAM 模型适配器
├── examples.py         # 使用示例
├── config.ini          # 配置文件
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档
```

## 配置文件说明

### 编辑 config.ini 修改参数

```ini
[model]
type = "default"          # 模型类型：default, large, huge
device = "auto"           # 运行设备：auto, cuda, cpu
model_paths = {}          # 自定义模型路径

[segmentation]
default_confidence_threshold = 0.5    # 置信度阈值
min_mask_area_ratio = 0.01           # 最小掩码面积比例
max_masks = 10                        # 最大掩码数量
multimask_output = false             # 多掩码输出

[output]
default_background_color = "transparent"  # 默认背景颜色
default_output_format = "png"             # 默认输出格式
save_mask = true                          # 是否保存掩码
mask_suffix = "_mask"                     # 掩码文件名后缀

[batch]
batch_size = 4              # 批处理大小
skip_on_error = true        # 跳过错误文件

[advanced]
verbose = false             # 详细日志
enable_cache = false        # 启用缓存
```

### 代码中使用配置文件

```python
from sam_segment import create_segmenter

# 方式 1: 使用默认 config.ini
segmenter = create_segmenter()

# 方式 2: 使用自定义配置文件
segmenter = create_segmenter(config_path="./my_config.ini")

# 方式 3: 覆盖配置文件设置
segmenter = create_segmenter(
    config_path="./config.ini",
    model_type="large",  # 覆盖配置
    device="cuda"        # 覆盖配置
)

# 查看当前配置
config = segmenter.get_config()
print(f"模型类型：{config.model_type}")
print(f"置信度阈值：{config.confidence_threshold}")
```

### 命令行使用配置

```bash
# 使用配置文件默认值
python sam_segment.py input.jpg output.png

# 指定配置文件
python sam_segment.py input.jpg -c my_config.ini

# 覆盖配置文件设置
python sam_segment.py input.jpg -c config.ini -m large -d cuda -t 0.7

# 查看详细配置信息
python sam_segment.py input.jpg -v
```

## 常见问题

### Q: 模型加载失败怎么办？

A: 确保已下载对应的 `.pth` 模型文件，并检查路径是否正确。

### Q: 如何使用 GPU 加速？

A: 安装 CUDA 版本的 PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

然后在代码中指定 `device="cuda"`。

### Q: 分割效果不理想？

A: 尝试以下方法：
1. 使用更大的模型（`model_type="large"`）
2. 调整置信度阈值（`confidence_threshold=0.6`）
3. 使用点提示或框提示进行引导

### Q: 输出 JPEG 时背景变白色？

A: JPEG 格式不支持透明通道，如需透明背景请使用 PNG 格式。

## 许可证

本项目基于 Meta 的 SAM 模型构建。SAM 模型采用 [Apache 2.0 许可证](https://github.com/facebookresearch/segment-anything/blob/main/LICENSE)。

## 参考链接

- [SAM 官方仓库](https://github.com/facebookresearch/segment-anything)
- [SAM 论文](https://arxiv.org/abs/2304.02643)
- [SAM Demo](https://segment-anything.com/demo)
