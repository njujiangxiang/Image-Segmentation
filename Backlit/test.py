#!/usr/bin/env python3
"""
逆光检测工具 - 功能测试脚本
测试所有配置和功能模块
"""

import sys
import os

# 切换到 Backlit 目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试 1: 导入模块")
print("=" * 60)

try:
    from backlit_detector import (
        BacklitDetector,
        DetectionMethod,
        DetectionResult,
        detect_backlit,
        detect_backlit_batch
    )
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败：{e}")
    sys.exit(1)

# 测试 2: 创建检测器
print()
print("=" * 60)
print("测试 2: 创建检测器")
print("=" * 60)

try:
    detector = BacklitDetector()
    print("✓ 检测器创建成功")
    print(f"   配置项数量：{len(detector.config)}")
except Exception as e:
    print(f"✗ 检测器创建失败：{e}")
    sys.exit(1)

# 测试 3: 配置测试
print()
print("=" * 60)
print("测试 3: 配置测试")
print("=" * 60)

config = detector.config
print(f"直方图阈值：{config['histogram']['peak_distance_threshold']}")
print(f"空间分析阈值：{config['spatial']['center_edge_ratio_threshold']}")
print(f"光晕检测阈值：{config['halo']['halo_ratio_threshold']}")
print(f"综合置信度阈值：{config['comprehensive']['confidence_threshold']}")
print("✓ 配置读取成功")

# 测试 4: 更新配置测试
print()
print("=" * 60)
print("测试 4: 更新配置测试")
print("=" * 60)

try:
    detector.update_config({
        'histogram': {
            'peak_distance_threshold': 100
        }
    })
    new_threshold = detector.config['histogram']['peak_distance_threshold']
    print(f"更新后的直方图阈值：{new_threshold}")
    assert new_threshold == 100, "配置更新失败"
    print("✓ 配置更新成功")
except Exception as e:
    print(f"✗ 配置更新失败：{e}")
    sys.exit(1)

# 测试 5: DetectionMethod 枚举测试
print()
print("=" * 60)
print("测试 5: 检测方法枚举")
print("=" * 60)

methods = [
    DetectionMethod.HISTOGRAM,
    DetectionMethod.SPATIAL,
    DetectionMethod.HALO,
    DetectionMethod.CHROMINANCE,
    DetectionMethod.COMPREHENSIVE
]

for method in methods:
    print(f"  - {method.value}")
print("✓ 枚举测试通过")

# 测试 6: 便捷函数测试（不实际处理图片）
print()
print("=" * 60)
print("测试 6: 函数签名测试")
print("=" * 60)

import inspect

# 检查 detect_backlit 函数
sig = inspect.signature(detect_backlit)
print(f"detect_backlit 参数：{list(sig.parameters.keys())}")

# 检查 detect_backlit_batch 函数
sig = inspect.signature(detect_backlit_batch)
print(f"detect_backlit_batch 参数：{list(sig.parameters.keys())}")

print("✓ 函数签名测试通过")

# 测试 7: 加载配置文件测试
print()
print("=" * 60)
print("测试 7: 配置文件加载")
print("=" * 60)

try:
    detector_with_config = BacklitDetector(config_path="config.json")
    print("✓ 配置文件加载成功")
except Exception as e:
    print(f"✗ 配置文件加载失败：{e}")
    sys.exit(1)

# 总结
print()
print("=" * 60)
print("所有测试通过!")
print("=" * 60)
print()
print("使用说明:")
print("  1. 编辑 config.json 修改参数")
print("  2. 运行：python backlit_detector.py image.jpg")
print("  3. 批量检测：python backlit_detector.py *.jpg --batch")
print("  4. 查看示例：python examples.py")
print()
