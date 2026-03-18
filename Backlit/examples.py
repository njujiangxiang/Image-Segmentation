#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆光检测工具使用示例

展示如何使用 BacklitDetector 进行逆光照片检测。
"""

from backlit_detector import BacklitDetector, DetectionMethod, detect_backlit, detect_backlit_batch
from pathlib import Path
import os


def example_basic_detection():
    """示例 1: 基础单张检测"""
    print("=" * 60)
    print("示例 1: 基础单张检测")
    print("=" * 60)
    
    # 准备测试图像
    test_image = "test_backlit.jpg"
    
    if not Path(test_image).exists():
        print(f"⚠️  测试图像不存在：{test_image}")
        print("   请将测试图像放入当前目录后重新运行")
        print("   或使用命令行：python examples.py --image your_image.jpg\n")
        return
    
    # 使用便捷函数检测
    result = detect_backlit(test_image)
    
    print(f"📷 图像：{test_image}")
    print(f"   是否逆光：{'是 ✓' if result['is_backlit'] else '否 ✗'}")
    print(f"   置信度：{result['confidence']:.2%}")
    print(f"   检测方法：{result['method']}")
    print()


def example_different_methods():
    """示例 2: 使用不同检测方法"""
    print("=" * 60)
    print("示例 2: 使用不同检测方法对比")
    print("=" * 60)
    
    test_image = "test_backlit.jpg"
    
    if not Path(test_image).exists():
        print(f"⚠️  测试图像不存在：{test_image}\n")
        return
    
    detector = BacklitDetector()
    
    methods = [
        (DetectionMethod.HISTOGRAM, "直方图分析"),
        (DetectionMethod.SPATIAL, "空间分布分析"),
        (DetectionMethod.HALO, "边缘光晕检测"),
        (DetectionMethod.CHROMINANCE, "色度分析"),
        (DetectionMethod.COMPREHENSIVE, "综合评分")
    ]
    
    print(f"图像：{test_image}\n")
    
    for method, name in methods:
        result = detector.detect(test_image, method)
        status = "✓ 逆光" if result.is_backlit else "✗ 非逆光"
        print(f"{name:12s}: {status:10s} (置信度：{result.confidence:.2%})")
    
    print()


def example_batch_detection():
    """示例 3: 批量检测"""
    print("=" * 60)
    print("示例 3: 批量检测多张图像")
    print("=" * 60)
    
    # 查找当前目录下的所有图片
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path('.').glob(ext))
    
    # 排除示例文件本身
    image_files = [f for f in image_files if f.name != 'examples.py']
    
    if not image_files:
        print("⚠️  当前目录下没有找到图像文件")
        print("   请将图像文件放入当前目录后重新运行\n")
        return
    
    print(f"找到 {len(image_files)} 张图像，开始检测...\n")
    
    # 批量检测
    detector = BacklitDetector()
    results = detector.detect_batch(
        [str(f) for f in image_files],
        DetectionMethod.COMPREHENSIVE,
        output_json="detection_results.json"
    )
    
    # 统计
    backlit_count = sum(1 for r in results if r.is_backlit)
    non_backlit_count = len(results) - backlit_count
    
    print(f"\n📊 统计结果:")
    print(f"   总图像数：{len(results)}")
    print(f"   逆光照片：{backlit_count} ({backlit_count/len(results)*100:.1f}%)")
    print(f"   非逆光照片：{non_backlit_count} ({non_backlit_count/len(results)*100:.1f}%)")
    print()


def example_custom_config():
    """示例 4: 自定义配置"""
    print("=" * 60)
    print("示例 4: 自定义配置参数")
    print("=" * 60)
    
    test_image = "test_backlit.jpg"
    
    if not Path(test_image).exists():
        print(f"⚠️  测试图像不存在：{test_image}\n")
        return
    
    # 创建自定义配置
    custom_config = {
        'histogram': {
            'peak_distance_threshold': 100,  # 提高阈值，更严格
            'min_dark_ratio': 0.25,
            'min_bright_ratio': 0.25
        },
        'comprehensive': {
            'confidence_threshold': 0.6,  # 提高置信度阈值
            'vote_threshold': 4  # 需要 4 个方法都同意
        }
    }
    
    # 使用自定义配置创建检测器
    detector_strict = BacklitDetector()
    detector_strict.update_config(custom_config)
    
    # 使用默认配置创建检测器
    detector_default = BacklitDetector()
    
    print("配置对比:")
    print("  默认配置 vs 严格配置\n")
    
    result_default = detector_default.detect(test_image, DetectionMethod.COMPREHENSIVE)
    result_strict = detector_strict.detect(test_image, DetectionMethod.COMPREHENSIVE)
    
    print(f"默认配置：{'✓ 逆光' if result_default.is_backlit else '✗ 非逆光'} "
          f"(置信度：{result_default.confidence:.2%})")
    print(f"严格配置：{'✓ 逆光' if result_strict.is_backlit else '✗ 非逆光'} "
          f"(置信度：{result_strict.confidence:.2%})")
    print()


def example_detailed_analysis():
    """示例 5: 详细分析报告"""
    print("=" * 60)
    print("示例 5: 详细分析报告")
    print("=" * 60)
    
    test_image = "test_backlit.jpg"
    
    if not Path(test_image).exists():
        print(f"⚠️  测试图像不存在：{test_image}\n")
        return
    
    detector = BacklitDetector()
    
    # 执行综合检测
    result = detector.detect(test_image, DetectionMethod.COMPREHENSIVE)
    
    print(f"📷 图像：{test_image}")
    print(f"   最终判断：{'逆光照片 ✓' if result.is_backlit else '非逆光照片 ✗'}")
    print(f"   综合置信度：{result.confidence:.2%}")
    print()
    
    # 显示各方法详情
    print("📋 各检测方法详情:")
    print("-" * 60)
    
    methods_detail = result.details.get('methods', {})
    for method_name, method_result in methods_detail.items():
        status = "✓" if method_result['is_backlit'] else "✗"
        print(f"  {method_name:15s}: {status} (置信度：{method_result['confidence']:.2%})")
    
    print()
    print(f"🗳️  投票结果：{result.details.get('vote_count', 0)}/4 方法判定为逆光")
    print()
    
    # 显示直方图分析详情（最有参考价值）
    if 'histogram' in methods_detail:
        h_result = detector._detect_histogram(cv2.imread(str(test_image)))
        print("📊 直方图分析详情:")
        print(f"   暗部比例：{h_result.details['dark_ratio']:.2%}")
        print(f"   亮部比例：{h_result.details['bright_ratio']:.2%}")
        print(f"   峰值距离：{h_result.details['peak_distance']} (阈值：80)")
        print(f"   暗部峰值：{h_result.details['dark_peak']}")
        print(f"   亮部峰值：{h_result.details['bright_peak']}")
    
    print()


def example_command_line():
    """示例 6: 命令行使用"""
    print("=" * 60)
    print("示例 6: 命令行使用方式")
    print("=" * 60)
    
    print("""
命令行用法:

1. 检测单张图片（综合方法）:
   python backlit_detector.py image.jpg

2. 使用特定方法检测:
   python backlit_detector.py image.jpg --method histogram
   python backlit_detector.py image.jpg --method spatial
   python backlit_detector.py image.jpg --method halo
   python backlit_detector.py image.jpg --method chrominance

3. 批量检测:
   python backlit_detector.py *.jpg --batch

4. 批量检测并输出 JSON:
   python backlit_detector.py *.jpg --batch --output results.json

5. 使用自定义配置文件:
   python backlit_detector.py image.jpg --config config.json

6. 查看帮助:
   python backlit_detector.py --help
    """)
    print()


def example_integration():
    """示例 7: 集成到其他项目"""
    print("=" * 60)
    print("示例 7: 集成到其他项目")
    print("=" * 60)
    
    print("""
# 方式 1: 使用便捷函数
from backlit_detector import detect_backlit

result = detect_backlit("image.jpg")
if result['is_backlit']:
    print(f"逆光照片，置信度：{result['confidence']:.2%}")

# 方式 2: 使用检测器类
from backlit_detector import BacklitDetector, DetectionMethod

detector = BacklitDetector()
result = detector.detect("image.jpg", DetectionMethod.COMPREHENSIVE)

# 方式 3: 批量检测
from backlit_detector import detect_backlit_batch

images = ["img1.jpg", "img2.jpg", "img3.jpg"]
results = detect_backlit_batch(images, output_json="results.json")

# 方式 4: 自定义配置
from backlit_detector import BacklitDetector

custom_config = {
    'comprehensive': {
        'confidence_threshold': 0.7  # 提高阈值
    }
}
detector = BacklitDetector()
detector.update_config(custom_config)

# 方式 5: 集成到图像处理流程
import cv2
from backlit_detector import BacklitDetector

def process_image(image_path):
    # 检测是否逆光
    detector = BacklitDetector()
    result = detector.detect(image_path)
    
    if result.is_backlit:
        # 逆光照片，进行特殊处理
        img = cv2.imread(image_path)
        # ... 逆光增强处理
    else:
        # 正常照片，标准处理
        # ...
    """)
    print()


def main():
    """运行所有示例"""
    print("\n🔦 逆光检测工具使用示例\n")
    
    # 检查依赖
    try:
        import cv2
        import numpy as np
        print("✅ 依赖检查通过 (OpenCV, NumPy)\n")
    except ImportError as e:
        print(f"❌ 缺少依赖：{e}")
        print("   请运行：pip install opencv-python numpy\n")
        return
    
    # 运行示例
    example_basic_detection()
    example_different_methods()
    example_batch_detection()
    example_custom_config()
    example_detailed_analysis()
    example_command_line()
    example_integration()
    
    print("=" * 60)
    print("🎉 所有示例运行完成!")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 将测试图片放入当前目录运行示例")
    print("   - 使用 --image 参数指定图片：python examples.py --image your_photo.jpg")
    print("   - 查看 backlit_detector.py 了解更多用法")
    print()


if __name__ == "__main__":
    import sys
    
    # 支持命令行参数 --image
    if len(sys.argv) > 1 and sys.argv[1] == '--image':
        if len(sys.argv) > 2:
            test_image = sys.argv[2]
            if Path(test_image).exists():
                result = detect_backlit(test_image)
                print(f"📷 图像：{test_image}")
                print(f"   是否逆光：{'是 ✓' if result['is_backlit'] else '否 ✗'}")
                print(f"   置信度：{result['confidence']:.2%}")
                print(f"   检测方法：{result['method']}")
            else:
                print(f"❌ 图像文件不存在：{test_image}")
        else:
            print("❌ 请指定图像路径：python examples.py --image image.jpg")
    else:
        main()
