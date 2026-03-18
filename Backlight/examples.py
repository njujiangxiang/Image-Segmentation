#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆光处理器调用示例 (Usage Examples)

本文件展示了如何使用 BacklightProcessor 处理逆光图片的各种场景。
包含 11 个完整示例，涵盖从基础用法到高级配置的所有场景。
"""

import cv2
import numpy as np
from backlight_processor import BacklightProcessor, load_config


def example_basic_usage():
    """
    示例 1: 基本用法 - 使用默认参数处理图片

    最简单的使用方式，适合快速测试和一般逆光场景。
    """
    print("=" * 50)
    print("示例 1: 基本用法")
    print("=" * 50)

    # 创建处理器（使用默认配置）
    processor = BacklightProcessor()

    # 读取图片
    image = cv2.imread("input.jpg")

    # 处理图片（使用默认完整流程）
    result = processor.process(image)

    # 保存结果
    cv2.imwrite("output.jpg", result)
    print("处理完成！")


def example_custom_config():
    """
    示例 2: 自定义配置 - 通过字典传入参数

    适合需要精细控制处理效果的场景。
    """
    print("=" * 50)
    print("示例 2: 自定义配置")
    print("=" * 50)

    # 自定义配置参数
    config = {
        "gamma": 1.8,              # 更强的 Gamma 校正
        "clip_limit": 3.0,         # 更高的对比度限制
        "brightness_factor": 1.5,  # 更强的亮度增强
        "hdr_strength": 0.5,       # 适中的 HDR 强度
    }

    # 使用自定义配置创建处理器
    processor = BacklightProcessor(config=config)

    image = cv2.imread("input.jpg")
    result = processor.process(image)
    cv2.imwrite("output_custom.jpg", result)
    print("使用自定义配置处理完成！")


def example_load_config_file():
    """
    示例 3: 从配置文件加载 - 使用 JSON 配置文件

    适合需要重复使用相同配置的场景。
    """
    print("=" * 50)
    print("示例 3: 从配置文件加载")
    print("=" * 50)

    # 从 JSON 文件加载配置
    config = load_config("config.json")

    # 创建处理器
    processor = BacklightProcessor(config=config)

    image = cv2.imread("input.jpg")
    result = processor.process(image)
    cv2.imwrite("output_config.jpg", result)
    print("使用配置文件处理完成！")


def example_different_methods():
    """
    示例 4: 不同处理方法对比 - 尝试各种算法效果

    适合测试不同方法的效果，找到最适合的处理方式。
    """
    print("=" * 50)
    print("示例 4: 不同处理方法对比")
    print("=" * 50)

    processor = BacklightProcessor()
    image = cv2.imread("input.jpg")

    # 尝试所有处理方法
    methods = {
        "gamma": "Gamma 校正 - 整体提亮",
        "clahe": "CLAHE - 增强局部对比度",
        "shadow": "阴影增强 - 选择性提亮暗部",
        "hdr": "HDR 风格 - 多尺度融合",
        "blend": "自适应混合 - 推荐",
        "all": "完整流程 - 最强效果",
    }

    for method, description in methods.items():
        result = processor.process(image, method=method)
        cv2.imwrite(f"output_{method}.jpg", result)
        print(f"  {method}: {description} -> output_{method}.jpg")


def example_mild_backlight():
    """
    示例 5: 轻度逆光图片处理 - 温和的参数

    适合逆光程度不严重的图片，保持自然效果。
    """
    print("=" * 50)
    print("示例 5: 轻度逆光图片处理")
    print("=" * 50)

    config = {
        "gamma": 1.3,              # 轻微的 Gamma 校正
        "clip_limit": 1.5,         # 较低的对比度限制
        "brightness_factor": 1.1,  # 轻微的亮度增强
    }

    processor = BacklightProcessor(config=config)
    image = cv2.imread("mild_backlight.jpg")

    # 使用自适应混合方法，效果自然
    result = processor.process(image, method="blend")
    cv2.imwrite("output_mild.jpg", result)
    print("轻度逆光处理完成！")


def example_severe_backlight():
    """
    示例 6: 严重逆光图片处理 - 强力的参数

    适合逆光非常严重的图片，最大程度恢复暗部细节。
    """
    print("=" * 50)
    print("示例 6: 严重逆光图片处理")
    print("=" * 50)

    config = {
        "gamma": 2.0,              # 强力的 Gamma 校正
        "clip_limit": 4.0,         # 高对比度限制
        "tile_grid_size": 6,       # 更小的网格，更局部的增强
        "brightness_factor": 1.8,  # 强力亮度增强
        "shadow_threshold": 0.4,   # 扩大阴影检测范围
    }

    processor = BacklightProcessor(config=config)
    image = cv2.imread("severe_backlight.jpg")

    # 使用完整处理流程
    result = processor.process(image, method="all")
    cv2.imwrite("output_severe.jpg", result)
    print("严重逆光处理完成！")


def example_hdr_landscape():
    """
    示例 7: 风景照片 HDR 效果 - 保留高光和阴影细节

    适合大光比的风景照片，如日出日落场景。
    """
    print("=" * 50)
    print("示例 7: 风景照片 HDR 效果")
    print("=" * 50)

    config = {
        "hdr_strength": 0.6,       # 适中的 HDR 强度
        "gamma": 1.4,
    }

    processor = BacklightProcessor(config=config)
    image = cv2.imread("landscape.jpg")

    # 使用 HDR 风格处理
    result = processor.process(image, method="hdr")
    cv2.imwrite("output_hdr_landscape.jpg", result)
    print("风景 HDR 处理完成！")


def example_portrait_backlight():
    """
    示例 8: 人像逆光处理 - 提亮面部同时保持背景

    适合逆光人像照片，提亮面部同时保持背景不过曝。
    """
    print("=" * 50)
    print("示例 8: 人像逆光处理")
    print("=" * 50)

    config = {
        "gamma": 1.5,
        "clip_limit": 2.0,
        "brightness_factor": 1.3,
        "shadow_threshold": 0.35,    # 精确的阴影检测
        "blur_kernel_size": 61,      # 更大的模糊核，更平滑的过渡
    }

    processor = BacklightProcessor(config=config)
    image = cv2.imread("portrait.jpg")

    # 使用自适应混合，自然提亮面部
    result = processor.process(image, method="blend")
    cv2.imwrite("output_portrait.jpg", result)
    print("人像逆光处理完成！")


def example_batch_processing():
    """
    示例 9: 批量处理 - 处理整个目录的图片

    适合批量处理旅游照片、活动照片等大量图片。
    """
    print("=" * 50)
    print("示例 9: 批量处理")
    print("=" * 50)

    config = {
        "gamma": 1.5,
        "clip_limit": 2.0,
    }

    processor = BacklightProcessor(config=config)

    # 批量处理目录中的所有图片
    stats = processor.process_batch(
        input_dir="./input_photos/",
        output_dir="./output_photos/",
        method="all",
        overwrite=True  # 覆盖已存在的文件
    )

    # 打印统计信息
    print(f"\n批量处理统计:")
    print(f"  总文件数：{stats['total']}")
    print(f"  成功：{stats['success']}")
    print(f"  跳过：{stats['skipped']}")
    print(f"  失败：{stats['failed']}")

    if stats['errors']:
        print("\n错误详情:")
        for name, error in stats['errors']:
            print(f"  {name}: {error}")


def example_create_test_image():
    """
    示例 10: 创建测试图片并处理 - 用于测试和演示

    创建模拟逆光场景的测试图片，用于验证处理效果。
    """
    print("=" * 50)
    print("示例 10: 创建测试图片并处理")
    print("=" * 50)

    # 创建模拟逆光场景的测试图片
    h, w = 400, 600
    test_img = np.zeros((h, w, 3), dtype=np.uint8)

    # 创建中心亮、四周暗的渐变背景 (模拟逆光)
    for y in range(h):
        for x in range(w):
            dist = np.sqrt((x - w/2)**2 + (y - h/2)**2)
            brightness = min(255, int(100 + 150 * dist / (w/2)))
            test_img[y, x] = [brightness, brightness, brightness]

    # 添加一个暗的前景矩形 (模拟逆光主体)
    cv2.rectangle(test_img, (200, 150), (400, 350), (50, 50, 50), -1)

    # 保存测试图片
    cv2.imwrite("test_input.jpg", test_img)
    print("测试图片已创建：test_input.jpg")

    # 创建处理器并处理
    processor = BacklightProcessor()
    result = processor.process(test_img, method="all")
    cv2.imwrite("test_output.jpg", result)
    print("测试图片处理完成：test_output.jpg")


def example_parameter_tuning():
    """
    示例 11: 参数调优 - 为特定图片找到最佳参数

    通过尝试不同参数值，找到最适合的处理效果。
    """
    print("=" * 50)
    print("示例 11: 参数调优")
    print("=" * 50)

    image = cv2.imread("input.jpg")

    # 尝试不同的 gamma 值
    gamma_values = [1.3, 1.5, 1.8, 2.0]
    for gamma in gamma_values:
        processor = BacklightProcessor({"gamma": gamma})
        result = processor.process(image, method="gamma")
        cv2.imwrite(f"output_gamma_{gamma}.jpg", result)
        print(f"  Gamma {gamma} -> output_gamma_{gamma}.jpg")

    # 尝试不同的 CLAHE 限制值
    clip_values = [1.5, 2.0, 3.0, 4.0]
    for clip in clip_values:
        processor = BacklightProcessor({"clip_limit": clip})
        result = processor.process(image, method="clahe")
        cv2.imwrite(f"output_clahe_{clip}.jpg", result)
        print(f"  CLAHE {clip} -> output_clahe_{clip}.jpg")


def main():
    """
    主函数 - 运行所有示例

    默认只运行测试图片示例 (示例 10)，
    其他示例需要实际的图片文件，可取消注释运行。
    """
    print("\n" + "=" * 60)
    print("逆光处理器调用示例")
    print("Backlight Processor Usage Examples")
    print("=" * 60 + "\n")

    # 运行示例 10（创建测试图片并处理）
    # 其他示例需要实际的图片文件，取消注释前请确保图片存在
    example_create_test_image()

    # 取消以下注释来运行其他示例（需要对应的图片文件）
    # example_basic_usage()
    # example_custom_config()
    # example_load_config_file()
    # example_different_methods()
    # example_mild_backlight()
    # example_severe_backlight()
    # example_hdr_landscape()
    # example_portrait_backlight()
    # example_batch_processing()
    # example_parameter_tuning()

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
