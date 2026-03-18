#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆光图像处理器 (Backlight Image Processor)

用于处理逆光拍摄的图片，通过多种算法增强图像亮度和对比度，
使暗部细节更清晰，同时保持高光区域不过曝。

功能特性:
    - Gamma 校正：调整图像整体亮度
    - CLAHE：限制对比度自适应直方图均衡化
    - 阴影增强：选择性提亮暗部区域
    - HDR 风格：多尺度融合模拟 HDR 效果
    - 自适应混合：根据亮度自适应调整处理强度

作者：Claude
创建日期：2026-03-18
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np


class BacklightProcessor:
    """
    逆光图像处理器

    提供多种逆光图像增强算法，可单独使用或组合使用。

    Attributes:
        config: 配置字典，包含所有处理参数
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化处理器

        Args:
            config: 配置字典，可选。包含以下参数:
                - gamma: Gamma 校正值 (默认 1.5)
                - clip_limit: CLAHE 限制值 (默认 2.0)
                - tile_grid_size: CLAHE 网格大小 (默认 8)
                - blur_kernel_size: 模糊核大小 (默认 51)
                - brightness_factor: 亮度增强系数 (默认 1.2)
                - shadow_threshold: 阴影阈值 (默认 0.3)
                - highlight_threshold: 高光阈值 (默认 0.8)
                - hdr_strength: HDR 强度 (默认 0.7)
        """
        # 默认配置参数
        self.config = {
            'gamma': 1.5,
            'clip_limit': 2.0,
            'tile_grid_size': 8,
            'blur_kernel_size': 51,
            'brightness_factor': 1.2,
            'shadow_threshold': 0.3,
            'highlight_threshold': 0.8,
            'hdr_strength': 0.7,
        }

        # 如果提供了配置，更新默认值
        if config:
            self.config.update(config)

        # 确保模糊核大小为奇数 (高斯模糊要求)
        if self.config['blur_kernel_size'] % 2 == 0:
            self.config['blur_kernel_size'] += 1

    def gamma_correction(self, image: np.ndarray, gamma: Optional[float] = None) -> np.ndarray:
        """
        应用 Gamma 校正调整图像亮度

        Gamma 校正公式：output = input ^ (1/gamma)
        - gamma > 1: 图像变亮 (适合逆光图片)
        - gamma < 1: 图像变暗

        Args:
            image: 输入图像 (BGR 格式，numpy 数组)
            gamma: Gamma 值，None 时使用配置值

        Returns:
            Gamma 校正后的图像 (BGR 格式)
        """
        gamma = gamma if gamma is not None else self.config['gamma']

        # 构建查找表 (LUT) 以加速计算
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                         for i in np.arange(0, 256)]).astype("uint8")

        # 对每个通道应用查找表
        return cv2.LUT(image, table)

    def apply_clahe(self, image: np.ndarray,
                    clip_limit: Optional[float] = None,
                    tile_grid_size: Optional[int] = None) -> np.ndarray:
        """
        应用 CLAHE (限制对比度自适应直方图均衡化)

        CLAHE 可以增强局部对比度，同时避免过度放大噪声。
        在 Lab 色彩空间的 L 通道 (亮度) 上应用，保持色彩不变。

        Args:
            image: 输入图像 (BGR 格式)
            clip_limit: 对比度限制值，越高对比度越强
            tile_grid_size: 网格大小，越小局部增强越明显

        Returns:
            CLAHE 处理后的图像 (BGR 格式)
        """
        clip_limit = clip_limit if clip_limit is not None else self.config['clip_limit']
        tile_grid_size = tile_grid_size if tile_grid_size is not None else self.config['tile_grid_size']

        # 创建 CLAHE 对象
        clahe = cv2.createCLAHE(clipLimit=clip_limit,
                                tileGridSize=(tile_grid_size, tile_grid_size))

        # 转换到 Lab 色彩空间
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # 只对 L 通道 (亮度) 应用 CLAHE
        l_channel = lab[:, :, 0]
        l_enhanced = clahe.apply(l_channel)

        # 合并通道并转换回 BGR
        lab[:, :, 0] = l_enhanced
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def shadow_enhancement(self, image: np.ndarray,
                           brightness_factor: Optional[float] = None,
                           blur_kernel_size: Optional[int] = None) -> np.ndarray:
        """
        阴影增强处理

        通过创建模糊的亮度掩膜，有选择性地提亮暗部区域，
        同时保持高光区域不受影响。适合处理前景太暗的逆光图片。

        Args:
            image: 输入图像 (BGR 格式)
            brightness_factor: 亮度增强系数，越高暗部提亮越明显
            blur_kernel_size: 高斯模糊核大小，必须是奇数

        Returns:
            阴影增强后的图像 (BGR 格式)
        """
        brightness_factor = brightness_factor if brightness_factor is not None else self.config['brightness_factor']
        blur_kernel_size = blur_kernel_size if blur_kernel_size is not None else self.config['blur_kernel_size']

        # 转换到 HSV 色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 提取 V 通道 (亮度)
        v_channel = hsv[:, :, 2].astype(np.float32)

        # 创建模糊的亮度掩膜
        blurred = cv2.GaussianBlur(v_channel, (blur_kernel_size, blur_kernel_size), 0)

        # 计算亮度比率
        # 暗部区域比率大，亮部区域比率小
        ratio = (v_channel.mean() + 1) / (blurred + 1)
        ratio = np.clip(ratio * brightness_factor, 0, 255 / (v_channel.max() + 1))

        # 应用增强
        v_enhanced = v_channel * ratio

        # 限制值范围
        v_enhanced = np.clip(v_enhanced, 0, 255).astype(np.uint8)

        # 合并通道并转换回 BGR
        hsv[:, :, 2] = v_enhanced
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def hdr_like_enhancement(self, image: np.ndarray,
                             strength: Optional[float] = None) -> np.ndarray:
        """
        模拟 HDR 效果

        通过多尺度融合模拟 HDR 成像效果，增强细节同时保持动态范围。
        适合大光比场景，如日出日落、室内逆光等。

        Args:
            image: 输入图像 (BGR 格式)
            strength: HDR 强度 (0-1)，0 为原图，1 为最强效果

        Returns:
            HDR 风格处理后的图像 (BGR 格式)
        """
        strength = strength if strength is not None else self.config['hdr_strength']
        strength = np.clip(strength, 0, 1)

        # 创建多尺度模糊图像
        images = []
        scales = [1, 0.5, 0.25]

        for scale in scales:
            h, w = image.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)

            # 缩小
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            # 高斯模糊
            blurred = cv2.GaussianBlur(resized, (0, 0), sigmaX=10 * scale)
            # 恢复原尺寸
            restored = cv2.resize(blurred, (w, h), interpolation=cv2.INTER_CUBIC)
            images.append(restored)

        # 融合
        result = np.zeros_like(image, dtype=np.float32)
        weights = [0.5, 0.3, 0.2]

        for img, weight in zip(images, weights):
            result += img.astype(np.float32) * weight * strength

        # 与原图混合
        result = image.astype(np.float32) * (1 - strength) + result
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    def adaptive_blend(self, image: np.ndarray,
                       shadow_threshold: Optional[float] = None,
                       highlight_threshold: Optional[float] = None) -> np.ndarray:
        """
        自适应混合处理

        根据像素亮度自适应地混合不同处理结果：
        - 暗部区域：应用较强的阴影增强
        - 中间调：应用 Gamma 校正和 CLAHE
        - 高光区域：保持原图，避免过曝

        Args:
            image: 输入图像 (BGR 格式)
            shadow_threshold: 阴影阈值 (0-1)，低于此值认为是阴影
            highlight_threshold: 高光阈值 (0-1)，高于此值认为是高光

        Returns:
            自适应混合后的图像 (BGR 格式)
        """
        shadow_threshold = shadow_threshold if shadow_threshold is not None else self.config['shadow_threshold']
        highlight_threshold = highlight_threshold if highlight_threshold is not None else self.config['highlight_threshold']

        # 计算亮度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        # 创建权重图
        # 暗部权重高，亮部权重低
        shadow_weight = np.clip((shadow_threshold - gray) / shadow_threshold, 0, 1)
        highlight_weight = np.clip((gray - highlight_threshold) / (1 - highlight_threshold), 0, 1)

        # 获取不同处理结果
        gamma_corrected = self.gamma_correction(image)
        clahe_result = self.apply_clahe(image)
        shadow_result = self.shadow_enhancement(image)

        # 基础处理结果 (Gamma + CLAHE)
        base_result = cv2.addWeighted(gamma_corrected, 0.5, clahe_result, 0.5, 0)

        # 转换为 float 进行混合
        base_result = base_result.astype(np.float32)
        shadow_result = shadow_result.astype(np.float32)
        image = image.astype(np.float32)

        # 自适应混合权重
        blend_weight = shadow_weight * 0.7 + (1 - highlight_weight) * 0.3
        blend_weight = np.clip(blend_weight, 0, 1)

        # 扩展权重到 3 通道
        blend_weight_3ch = np.stack([blend_weight] * 3, axis=2)

        # 混合结果
        result = image * (1 - blend_weight_3ch) + shadow_result * blend_weight_3ch
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    def process(self, image: np.ndarray, method: str = 'all') -> np.ndarray:
        """
        处理逆光图像

        Args:
            image: 输入图像 (BGR 格式，通过 cv2.imread 读取)
            method: 处理方法，可选值:
                - 'gamma': 仅 Gamma 校正
                - 'clahe': 仅 CLAHE
                - 'shadow': 仅阴影增强
                - 'hdr': 仅 HDR 风格
                - 'blend': 自适应混合 (推荐)
                - 'all': 完整处理流程 (默认)

        Returns:
            处理后的图像 (BGR 格式)

        Raises:
            ValueError: 当 method 参数不是有效值时
        """
        if method == 'gamma':
            return self.gamma_correction(image)
        elif method == 'clahe':
            return self.apply_clahe(image)
        elif method == 'shadow':
            return self.shadow_enhancement(image)
        elif method == 'hdr':
            return self.hdr_like_enhancement(image)
        elif method == 'blend':
            return self.adaptive_blend(image)
        elif method == 'all':
            # 完整处理流程：Gamma -> CLAHE -> 阴影增强
            result = self.gamma_correction(image)
            result = self.apply_clahe(result)
            result = self.shadow_enhancement(result)
            return result
        else:
            raise ValueError(f"未知处理方法：{method}。有效值：gamma, clahe, shadow, hdr, blend, all")

    def process_batch(self, input_dir: str, output_dir: str,
                      method: str = 'all', overwrite: bool = False) -> Dict:
        """
        批量处理目录中的图片

        支持的格式：JPG, JPEG, PNG, BMP, TIFF, TIF, WebP

        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            method: 处理方法 (默认 'all')
            overwrite: 是否覆盖已存在的文件 (默认 False)

        Returns:
            处理统计信息字典:
                - total: 总文件数
                - success: 成功数量
                - failed: 失败数量
                - skipped: 跳过数量
                - errors: 错误列表 [(文件名，错误信息), ...]
        """
        # 支持的图片格式
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 统计信息
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        # 遍历输入目录
        for file_path in Path(input_dir).iterdir():
            if file_path.suffix.lower() not in extensions:
                continue

            stats['total'] += 1
            output_path = Path(output_dir) / file_path.name

            # 检查是否已存在
            if output_path.exists() and not overwrite:
                print(f"跳过已存在的文件：{output_path}")
                stats['skipped'] += 1
                continue

            try:
                # 读取图像
                image = cv2.imread(str(file_path))
                if image is None:
                    raise ValueError("无法读取图像，文件格式可能不支持")

                # 处理图像
                result = self.process(image, method)

                # 保存结果，根据格式设置压缩参数
                save_params = []
                if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
                    save_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
                elif output_path.suffix.lower() == '.png':
                    save_params = [cv2.IMWRITE_PNG_COMPRESSION, 6]

                cv2.imwrite(str(output_path), result, save_params)

                print(f"处理完成：{file_path.name}")
                stats['success'] += 1

            except Exception as e:
                print(f"处理失败：{file_path.name} - {str(e)}")
                stats['failed'] += 1
                stats['errors'].append((file_path.name, str(e)))

        return stats


def load_config(config_path: str) -> Dict:
    """
    从 JSON 文件加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: Dict, config_path: str):
    """
    保存配置到 JSON 文件

    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def main():
    """
    主函数 - 命令行入口

    支持单张处理和批量处理两种模式。
    所有参数可通过配置文件或命令行指定。
    """
    parser = argparse.ArgumentParser(
        description='逆光图像处理器 - 增强逆光拍摄的图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 处理单张图片 (使用默认参数)
  python backlight_processor.py input.jpg output.jpg

  # 使用自定义参数
  python backlight_processor.py input.jpg output.jpg --gamma 2.0 --brightness 1.5

  # 批量处理目录
  python backlight_processor.py ./input_images/ ./output_images/ --batch

  # 使用配置文件
  python backlight_processor.py input.jpg output.jpg --config config.json

  # 使用指定处理方法
  python backlight_processor.py input.jpg output.jpg --method blend

  # 生成默认配置文件
  python backlight_processor.py dummy dummy --generate-config config.json
        """
    )

    # 位置参数
    parser.add_argument('input', help='输入图片路径或输入目录 (批量处理时)')
    parser.add_argument('output', help='输出图片路径或输出目录 (批量处理时)')

    # 可选参数
    parser.add_argument('--batch', action='store_true',
                        help='批量处理模式')
    parser.add_argument('--config', type=str,
                        help='配置文件路径 (JSON 格式)')
    parser.add_argument('--method', type=str,
                        choices=['gamma', 'clahe', 'shadow', 'hdr', 'blend', 'all'],
                        default='all',
                        help='处理方法 (默认：all)')
    parser.add_argument('--overwrite', action='store_true',
                        help='覆盖已存在的输出文件')

    # 图像参数
    parser.add_argument('--gamma', type=float, default=None,
                        help='Gamma 校正值 (默认：1.5)')
    parser.add_argument('--clip-limit', type=float, default=None, dest='clip_limit',
                        help='CLAHE 对比度限制 (默认：2.0)')
    parser.add_argument('--tile-grid', type=int, default=None, dest='tile_grid',
                        help='CLAHE 网格大小 (默认：8)')
    parser.add_argument('--blur-kernel', type=int, default=None, dest='blur_kernel',
                        help='模糊核大小 (默认：51)')
    parser.add_argument('--brightness', type=float, default=None,
                        help='亮度增强系数 (默认：1.2)')
    parser.add_argument('--shadow-threshold', type=float, default=None,
                        help='阴影阈值 (默认：0.3)')
    parser.add_argument('--highlight-threshold', type=float, default=None,
                        help='高光阈值 (默认：0.8)')
    parser.add_argument('--hdr-strength', type=float, default=None,
                        help='HDR 强度 (默认：0.7)')

    # 生成默认配置
    parser.add_argument('--generate-config', type=str, metavar='CONFIG_FILE',
                        help='生成默认配置文件并退出')

    args = parser.parse_args()

    # 生成配置文件
    if args.generate_config:
        default_config = {
            'gamma': 1.5,
            'clip_limit': 2.0,
            'tile_grid_size': 8,
            'blur_kernel_size': 51,
            'brightness_factor': 1.2,
            'shadow_threshold': 0.3,
            'highlight_threshold': 0.8,
            'hdr_strength': 0.7,
        }
        save_config(default_config, args.generate_config)
        print(f"默认配置文件已生成：{args.generate_config}")
        return

    # 加载配置
    config = {}
    if args.config:
        config = load_config(args.config)
        print(f"已加载配置文件：{args.config}")

    # 命令行参数覆盖配置文件
    if args.gamma is not None:
        config['gamma'] = args.gamma
    if args.clip_limit is not None:
        config['clip_limit'] = args.clip_limit
    if args.tile_grid is not None:
        config['tile_grid_size'] = args.tile_grid
    if args.blur_kernel is not None:
        config['blur_kernel_size'] = args.blur_kernel
    if args.brightness is not None:
        config['brightness_factor'] = args.brightness
    if args.shadow_threshold is not None:
        config['shadow_threshold'] = args.shadow_threshold
    if args.highlight_threshold is not None:
        config['highlight_threshold'] = args.highlight_threshold
    if args.hdr_strength is not None:
        config['hdr_strength'] = args.hdr_strength

    # 创建处理器
    processor = BacklightProcessor(config)

    # 处理图像
    if args.batch:
        # 批量处理
        if not os.path.isdir(args.input):
            print(f"错误：输入路径必须是目录：{args.input}")
            return

        stats = processor.process_batch(
            args.input, args.output,
            method=args.method,
            overwrite=args.overwrite
        )

        print("\n" + "=" * 40)
        print("处理统计:")
        print(f"  总文件数：{stats['total']}")
        print(f"  成功：{stats['success']}")
        print(f"  跳过：{stats['skipped']}")
        print(f"  失败：{stats['failed']}")

        if stats['errors']:
            print("\n错误详情:")
            for name, error in stats['errors']:
                print(f"  {name}: {error}")
    else:
        # 单张处理
        if not os.path.isfile(args.input):
            print(f"错误：输入文件不存在：{args.input}")
            return

        # 确保输出目录存在
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        print(f"处理图片：{args.input}")

        # 读取图像
        image = cv2.imread(args.input)
        if image is None:
            print(f"错误：无法读取图像：{args.input}")
            return

        # 处理图像
        result = processor.process(image, method=args.method)

        # 保存结果
        cv2.imwrite(args.output, result)
        print(f"处理完成，结果已保存：{args.output}")


if __name__ == '__main__':
    main()
