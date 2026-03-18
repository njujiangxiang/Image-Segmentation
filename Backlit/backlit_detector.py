#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆光照片检测工具

基于多种算法检测和识别逆光拍摄的图像，支持：
- 亮度直方图分析
- 空间亮度分布分析
- 边缘光晕检测
- 色度分析
- 综合评分

作者：小雨爸爸
日期：2026 年 3 月
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class DetectionMethod(Enum):
    """检测方法枚举"""
    HISTOGRAM = "histogram"
    SPATIAL = "spatial"
    HALO = "halo"
    CHROMINANCE = "chrominance"
    COMPREHENSIVE = "comprehensive"


@dataclass
class DetectionResult:
    """检测结果数据类"""
    is_backlit: bool
    confidence: float
    method: str
    details: Dict[str, Any]


class BacklitDetector:
    """逆光照片检测器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化检测器

        Args:
            config_path: 配置文件路径，默认使用内置配置
        """
        self.config = self._load_default_config()
        if config_path:
            self._load_config(config_path)

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            'histogram': {
                'peak_distance_threshold': 80,
                'min_dark_ratio': 0.2,
                'min_bright_ratio': 0.2,
                'peak_ratio_min': 0.3,
                'peak_ratio_max': 3.0
            },
            'spatial': {
                'center_edge_ratio_threshold': 0.7,
                'center_size_ratio': 0.25
            },
            'halo': {
                'halo_ratio_threshold': 1.3,
                'canny_threshold1': 50,
                'canny_threshold2': 150
            },
            'chrominance': {
                'saturation_diff_threshold': 30,
                'bright_threshold': 200,
                'dark_threshold': 80
            },
            'comprehensive': {
                'weights': {
                    'histogram': 0.35,
                    'spatial': 0.30,
                    'halo': 0.20,
                    'chrominance': 0.15
                },
                'confidence_threshold': 0.5,
                'vote_threshold': 3
            }
        }

    def _load_config(self, config_path: str) -> None:
        """从文件加载配置"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 深度合并配置
                self._merge_config(user_config)

    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """合并用户配置到默认配置"""
        for section, values in user_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values

    def detect(self, image_path: str, method: DetectionMethod = DetectionMethod.COMPREHENSIVE) -> DetectionResult:
        """
        检测图像是否为逆光照片

        Args:
            image_path: 图像文件路径
            method: 检测方法

        Returns:
            检测结果
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图像文件不存在：{image_path}")

        # 读取图像
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"无法读取图像：{image_path}")

        # 根据方法执行检测
        if method == DetectionMethod.HISTOGRAM:
            return self._detect_histogram(img)
        elif method == DetectionMethod.SPATIAL:
            return self._detect_spatial(img)
        elif method == DetectionMethod.HALO:
            return self._detect_halo(img)
        elif method == DetectionMethod.CHROMINANCE:
            return self._detect_chrominance(img)
        elif method == DetectionMethod.COMPREHENSIVE:
            return self._detect_comprehensive(img)
        else:
            raise ValueError(f"未知的检测方法：{method}")

    def _detect_histogram(self, img: np.ndarray) -> DetectionResult:
        """
        基于亮度直方图分析检测逆光

        原理：逆光图像的亮度直方图呈现明显的双峰分布
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算直方图
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # 归一化
        
        # 将直方图分为暗部和亮部（以 128 为界）
        dark_ratio = float(hist[:128].sum())
        bright_ratio = float(hist[128:].sum())
        
        # 计算直方图的双峰特性
        dark_peak = int(hist[:128].argmax())
        bright_peak = int(128 + hist[128:].argmax())
        
        # 计算峰值差异
        peak_distance = bright_peak - dark_peak
        peak_ratio = dark_ratio / bright_ratio if bright_ratio > 0 else float('inf')
        
        # 逆光判断条件
        cfg = self.config['histogram']
        is_backlit = (
            peak_distance > cfg['peak_distance_threshold'] and
            cfg['peak_ratio_min'] < peak_ratio < cfg['peak_ratio_max'] and
            dark_ratio > cfg['min_dark_ratio'] and
            bright_ratio > cfg['min_bright_ratio']
        )
        
        confidence = min(peak_distance / 128.0, 1.0)
        
        return DetectionResult(
            is_backlit=is_backlit,
            confidence=confidence,
            method="histogram",
            details={
                'dark_ratio': round(dark_ratio, 4),
                'bright_ratio': round(bright_ratio, 4),
                'peak_distance': peak_distance,
                'dark_peak': dark_peak,
                'bright_peak': bright_peak,
                'peak_ratio': round(peak_ratio, 4)
            }
        )

    def _detect_spatial(self, img: np.ndarray) -> DetectionResult:
        """
        基于空间亮度分布检测逆光

        原理：逆光照片的亮度分布有特定的空间模式（中心暗、边缘亮）
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        cfg = self.config['spatial']
        center_size = int(min(h, w) * cfg['center_size_ratio'])
        center_y, center_x = h // 2, w // 2
        
        # 中心区域亮度
        center_region = gray[
            center_y - center_size:center_y + center_size,
            center_x - center_size:center_x + center_size
        ]
        center_brightness = float(center_region.mean())
        
        # 边缘区域亮度（四个角）
        edge_size_h, edge_size_w = h // 3, w // 3
        corners = [
            gray[0:edge_size_h, 0:edge_size_w],
            gray[0:edge_size_h, w - edge_size_w:],
            gray[h - edge_size_h:, 0:edge_size_w],
            gray[h - edge_size_h:, w - edge_size_w:]
        ]
        edge_brightness = float(np.mean([corner.mean() for corner in corners]))
        
        # 计算中心 - 边缘亮度比
        brightness_ratio = center_brightness / edge_brightness if edge_brightness > 0 else 0
        
        # 逆光特征：中心比边缘暗
        is_backlit = brightness_ratio < cfg['center_edge_ratio_threshold']
        confidence = 1.0 - brightness_ratio
        
        return DetectionResult(
            is_backlit=is_backlit,
            confidence=max(confidence, 0.0),
            method="spatial",
            details={
                'center_brightness': round(center_brightness, 2),
                'edge_brightness': round(edge_brightness, 2),
                'brightness_ratio': round(brightness_ratio, 4)
            }
        )

    def _detect_halo(self, img: np.ndarray) -> DetectionResult:
        """
        检测主体边缘的光晕效应

        原理：逆光拍摄时，主体边缘常出现光晕/轮廓光
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cfg = self.config['halo']
        
        # Canny 边缘检测
        edges = cv2.Canny(gray, cfg['canny_threshold1'], cfg['canny_threshold2'])
        
        # 膨胀边缘
        kernel = np.ones((3, 3), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=2)
        
        # 创建边缘的掩码
        edge_mask = dilated_edges > 0
        
        # 计算边缘区域的平均亮度
        if edge_mask.sum() > 0:
            edge_brightness = float(gray[edge_mask].mean())
        else:
            edge_brightness = 0.0
        
        # 计算非边缘区域的平均亮度
        if (~edge_mask).sum() > 0:
            non_edge_brightness = float(gray[~edge_mask].mean())
        else:
            non_edge_brightness = 0.0
        
        # 如果边缘明显比周围亮，可能存在光晕
        halo_ratio = edge_brightness / non_edge_brightness if non_edge_brightness > 0 else 0
        is_backlit = halo_ratio > cfg['halo_ratio_threshold']
        
        confidence = min((halo_ratio - 1) / 0.5, 1.0) if halo_ratio > 1 else 0.0
        
        return DetectionResult(
            is_backlit=is_backlit,
            confidence=max(confidence, 0.0),
            method="halo",
            details={
                'edge_brightness': round(edge_brightness, 2),
                'non_edge_brightness': round(non_edge_brightness, 2),
                'halo_ratio': round(halo_ratio, 4),
                'edge_pixels': int(edge_mask.sum())
            }
        )

    def _detect_chrominance(self, img: np.ndarray) -> DetectionResult:
        """
        基于色度分析的逆光检测

        原理：逆光图像在高亮区域饱和度较低（参考 SPIE 论文）
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        
        cfg = self.config['chrominance']
        
        # 高亮区域和暗部区域
        bright_mask = value > cfg['bright_threshold']
        dark_mask = value < cfg['dark_threshold']
        
        # 计算饱和度
        bright_saturation = float(saturation[bright_mask].mean()) if bright_mask.sum() > 0 else 0.0
        dark_saturation = float(saturation[dark_mask].mean()) if dark_mask.sum() > 0 else 0.0
        
        # 逆光特征：亮部饱和度明显低于暗部
        sat_difference = dark_saturation - bright_saturation
        is_backlit = sat_difference > cfg['saturation_diff_threshold']
        
        confidence = min(sat_difference / 50.0, 1.0)
        
        return DetectionResult(
            is_backlit=is_backlit,
            confidence=max(confidence, 0.0),
            method="chrominance",
            details={
                'bright_saturation': round(bright_saturation, 2),
                'dark_saturation': round(dark_saturation, 2),
                'saturation_difference': round(sat_difference, 2),
                'bright_pixels': int(bright_mask.sum()),
                'dark_pixels': int(dark_mask.sum())
            }
        )

    def _detect_comprehensive(self, img: np.ndarray) -> DetectionResult:
        """
        综合多种方法的逆光检测

        原理：结合多种检测方法，给出综合判断
        """
        # 执行所有单项检测
        results = {
            'histogram': self._detect_histogram(img),
            'spatial': self._detect_spatial(img),
            'halo': self._detect_halo(img),
            'chrominance': self._detect_chrominance(img)
        }
        
        cfg = self.config['comprehensive']
        weights = cfg['weights']
        
        # 计算综合评分（加权平均）
        total_score = sum(
            results[method].confidence * weight
            for method, weight in weights.items()
        )
        
        # 投票机制
        vote_count = sum(1 for r in results.values() if r.is_backlit)
        
        # 综合判断
        is_backlit = total_score > cfg['confidence_threshold'] or vote_count >= cfg['vote_threshold']
        
        return DetectionResult(
            is_backlit=is_backlit,
            confidence=round(total_score, 4),
            method="comprehensive",
            details={
                'vote_count': vote_count,
                'total_score': round(total_score, 4),
                'weights': weights,
                'methods': {
                    method: {
                        'is_backlit': r.is_backlit,
                        'confidence': r.confidence
                    }
                    for method, r in results.items()
                }
            }
        )

    def detect_batch(self, image_paths: List[str], 
                     method: DetectionMethod = DetectionMethod.COMPREHENSIVE,
                     output_json: Optional[str] = None) -> List[DetectionResult]:
        """
        批量检测多张图像

        Args:
            image_paths: 图像文件路径列表
            method: 检测方法
            output_json: 输出结果 JSON 文件路径（可选）

        Returns:
            检测结果列表
        """
        results = []
        for img_path in image_paths:
            try:
                result = self.detect(img_path, method)
                results.append(result)
                print(f"✓ {Path(img_path).name}: {'逆光' if result.is_backlit else '非逆光'} "
                      f"(置信度：{result.confidence:.2%})")
            except Exception as e:
                print(f"✗ {Path(img_path).name}: 错误 - {e}")
                results.append(DetectionResult(
                    is_backlit=False,
                    confidence=0.0,
                    method=method.value,
                    details={'error': str(e)}
                ))
        
        # 输出 JSON 结果
        if output_json:
            self._save_results_to_json(results, output_json)
        
        return results

    def _save_results_to_json(self, results: List[DetectionResult], output_path: str) -> None:
        """将检测结果保存为 JSON 文件"""
        output_data = []
        for result in results:
            output_data.append({
                'is_backlit': result.is_backlit,
                'confidence': result.confidence,
                'method': result.method,
                'details': result.details
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到：{output_path}")

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config

    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self._merge_config(config)


def detect_backlit(image_path: str, method: str = "comprehensive") -> Dict[str, Any]:
    """
    便捷函数：检测单张图像是否为逆光照片

    Args:
        image_path: 图像文件路径
        method: 检测方法 (histogram/spatial/halo/chrominance/comprehensive)

    Returns:
        检测结果字典
    """
    detector = BacklitDetector()
    detect_method = DetectionMethod(method)
    result = detector.detect(image_path, detect_method)
    
    return {
        'is_backlit': result.is_backlit,
        'confidence': result.confidence,
        'method': result.method,
        'details': result.details
    }


def detect_backlit_batch(image_paths: List[str], output_json: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    便捷函数：批量检测图像

    Args:
        image_paths: 图像文件路径列表
        output_json: 输出结果 JSON 文件路径（可选）

    Returns:
        检测结果列表
    """
    detector = BacklitDetector()
    results = detector.detect_batch(image_paths, DetectionMethod.COMPREHENSIVE, output_json)
    
    return [
        {
            'is_backlit': r.is_backlit,
            'confidence': r.confidence,
            'method': r.method,
            'details': r.details
        }
        for r in results
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="逆光照片检测工具 - 检测和识别逆光拍摄的图像",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 检测单张图片
  python backlit_detector.py image.jpg

  # 使用特定方法检测
  python backlit_detector.py image.jpg --method histogram

  # 批量检测
  python backlit_detector.py *.jpg --batch

  # 批量检测并输出 JSON
  python backlit_detector.py *.jpg --batch --output results.json
        """
    )

    parser.add_argument("images", nargs="+", help="输入图像路径")
    parser.add_argument("--method", "-m", 
                       choices=["histogram", "spatial", "halo", "chrominance", "comprehensive"],
                       default="comprehensive",
                       help="检测方法，默认 comprehensive")
    parser.add_argument("--batch", "-b", action="store_true",
                       help="批量检测模式")
    parser.add_argument("--output", "-o", type=str, default=None,
                       help="输出结果 JSON 文件路径")
    parser.add_argument("--config", "-c", type=str, default=None,
                       help="配置文件路径")

    args = parser.parse_args()

    # 创建检测器
    detector = BacklitDetector(args.config) if args.config else BacklitDetector()

    if args.batch:
        # 批量检测
        results = detector.detect_batch(args.images, DetectionMethod(args.method), args.output)
        
        # 统计
        backlit_count = sum(1 for r in results if r.is_backlit)
        print(f"\n检测完成：共 {len(results)} 张图像，其中 {backlit_count} 张为逆光照片")
    else:
        # 单张检测
        if len(args.images) > 1:
            print("警告：非批量模式下只处理第一张图像")
        
        result = detector.detect(args.images[0], DetectionMethod(args.method))
        
        print(f"\n检测结果:")
        print(f"  图像：{args.images[0]}")
        print(f"  是否逆光：{'是 ✓' if result.is_backlit else '否 ✗'}")
        print(f"  置信度：{result.confidence:.2%}")
        print(f"  检测方法：{result.method}")
        print(f"\n详细信息:")
        for key, value in result.details.items():
            print(f"  {key}: {value}")
