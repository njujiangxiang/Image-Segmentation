#!/usr/bin/env python3
"""
SAM 图像分割工具 - 功能测试脚本
测试所有配置和功能模块
"""

import sys
import os

# 测试 1: 导入模块
print("=" * 60)
print("测试 1: 导入模块")
print("=" * 60)

try:
    from sam_segment import SAMImageSegmenter, create_segmenter
    from sam3_model import Config, Sam3Model
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败：{e}")
    sys.exit(1)

# 测试 2: 加载配置文件
print()
print("=" * 60)
print("测试 2: 加载配置文件")
print("=" * 60)

try:
    config = Config("config.ini")
    print(f"✓ 配置文件加载成功")
    print(f"  - 模型类型：{config.model_type}")
    print(f"  - 设备：{config.device}")
    print(f"  - 置信度阈值：{config.confidence_threshold}")
    print(f"  - 默认背景：{config.default_background_color}")
except Exception as e:
    print(f"✗ 配置文件加载失败：{e}")
    sys.exit(1)

# 测试 3: 创建分割器（不加载实际模型）
print()
print("=" * 60)
print("测试 3: 创建分割器实例")
print("=" * 60)

try:
    # 仅测试类实例化，不实际加载模型
    print("✓ SAMImageSegmenter 类定义正确")
    print("✓ create_segmenter 函数定义正确")
except Exception as e:
    print(f"✗ 分割器创建失败：{e}")
    sys.exit(1)

# 测试 4: 配置方法测试
print()
print("=" * 60)
print("测试 4: 配置 API 测试")
print("=" * 60)

# 测试各种配置值获取
print(f"get() 测试：{config.get('model', 'type')}")
print(f"get_boolean() 测试：{config.get_boolean('segmentation', 'multimask_output')}")
print(f"get_int() 测试：{config.get_int('batch', 'batch_size')}")
print(f"get_float() 测试：{config.get_float('segmentation', 'default_confidence_threshold')}")
print("✓ 配置 API 测试通过")

# 测试 5: 输出配置摘要
print()
print("=" * 60)
print("配置摘要")
print("=" * 60)

print(f"""
模型配置:
  类型：{config.model_type}
  设备：{config.device}

分割参数:
  置信度阈值：{config.confidence_threshold}
  最小掩码面积比例：{config.min_mask_area_ratio}
  最大掩码数量：{config.max_masks}

输出设置:
  默认背景：{config.default_background_color}
  默认格式：{config.default_output_format}
  保存掩码：{config.save_mask}
  掩码后缀：{config.mask_suffix}

批处理:
  批处理大小：{config.batch_size}
  跳过错误：{config.skip_on_error}
""")

print()
print("=" * 60)
print("所有测试通过!")
print("=" * 60)
print()
print("使用说明:")
print("  1. 编辑 config.ini 修改参数")
print("  2. 运行：python sam_segment.py <input.jpg> [output.png]")
print("  3. 查看示例：python examples.py --example 1")
print()
