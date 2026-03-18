"""
SAM 图像分割工具 - 使用示例

本文件包含多个使用示例，展示如何使用 SAM 图像分割工具
"""

from sam_segment import SAMImageSegmenter, create_segmenter, Config


def example_basic_usage():
    """示例 1: 基础用法 - 使用配置文件默认设置"""
    print("=" * 50)
    print("示例 1: 基础用法 - 使用配置文件默认设置")
    print("=" * 50)

    # 自动加载 config.ini 配置
    segmenter = create_segmenter()

    result = segmenter.segment(
        input_path="input.jpg",
        output_path="output_transparent.png"
    )

    if result["success"]:
        print(f"输出：{result['output_path']}")
        print(f"置信度：{result['confidence']:.2%}")
    else:
        print(f"失败：{result['message']}")


def example_custom_config_file():
    """示例 2: 使用自定义配置文件"""
    print("=" * 50)
    print("示例 2: 使用自定义配置文件")
    print("=" * 50)

    # 使用自定义配置文件
    segmenter = create_segmenter(config_path="./my_config.ini")

    result = segmenter.segment(
        input_path="input.jpg",
        output_path="output.png"
    )

    if result["success"]:
        print(f"输出：{result['output_path']}")
    else:
        print(f"失败：{result['message']}")


def example_override_config():
    """示例 3: 覆盖配置文件设置"""
    print("=" * 50)
    print("示例 3: 覆盖配置文件设置")
    print("=" * 50)

    # 使用配置文件，但覆盖某些设置
    segmenter = create_segmenter(
        config_path="./config.ini",
        model_type="large",  # 覆盖配置文件中的模型类型
        device="cuda"        # 覆盖配置文件中的设备
    )

    result = segmenter.segment(
        input_path="input.jpg",
        output_path="output_hq.png",
        background_color="transparent",
        confidence_threshold=0.7  # 覆盖配置文件中的阈值
    )

    if result["success"]:
        print(f"输出：{result['output_path']}")
        print(f"置信度：{result['confidence']:.2%}")


def example_black_background():
    """示例 4: 黑色背景"""
    print("=" * 50)
    print("示例 4: 黑色背景")
    print("=" * 50)

    segmenter = create_segmenter()

    result = segmenter.segment(
        input_path="input.jpg",
        output_path="output_black_bg.png",
        background_color="black"
    )

    if result["success"]:
        print(f"输出：{result['output_path']}")
    else:
        print(f"失败：{result['message']}")


def example_custom_background_color():
    """示例 5: 自定义背景颜色 (RGB)"""
    print("=" * 50)
    print("示例 5: 自定义背景颜色")
    print("=" * 50)

    segmenter = create_segmenter()

    # 使用 RGB 元组设置背景颜色 (例如：蓝色背景)
    result = segmenter.segment(
        input_path="input.jpg",
        output_path="output_blue_bg.png",
        background_color=(100, 149, 237)  # 矢车菊蓝
    )

    if result["success"]:
        print(f"输出：{result['output_path']}")
    else:
        print(f"失败：{result['message']}")


def example_view_config():
    """示例 6: 查看当前配置"""
    print("=" * 50)
    print("示例 6: 查看当前配置")
    print("=" * 50)

    segmenter = create_segmenter()
    config = segmenter.get_config()

    print(f"模型类型：{config.model_type}")
    print(f"设备：{config.device}")
    print(f"置信度阈值：{config.confidence_threshold}")
    print(f"默认背景：{config.default_background_color}")
    print(f"默认输出格式：{config.default_output_format}")
    print(f"保存掩码：{config.save_mask}")
    print(f"批处理大小：{config.batch_size}")


def example_batch_processing():
    """示例 7: 批量处理"""
    print("=" * 50)
    print("示例 7: 批量处理")
    print("=" * 50)

    segmenter = create_segmenter()

    input_images = [
        "images/photo1.jpg",
        "images/photo2.jpg",
        "images/photo3.jpg"
    ]

    results = segmenter.segment_batch(
        input_paths=input_images,
        output_dir="output_batch",
        background_color="white"
    )

    success_count = sum(1 for r in results if r["success"])
    print(f"处理完成：{success_count}/{len(results)} 成功")


def example_get_masks():
    """示例 8: 获取分割掩码"""
    print("=" * 50)
    print("示例 8: 获取分割掩码")
    print("=" * 50)

    segmenter = create_segmenter()

    # 获取所有可能的分割掩码
    masks = segmenter.get_masks(
        input_path="input.jpg",
        return_all=True
    )

    print(f"找到 {len(masks)} 个分割区域")
    for i, mask_info in enumerate(masks[:5]):  # 只显示前 5 个
        print(f"  区域 {i+1}: 置信度 = {mask_info['confidence']:.2%}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SAM 图像分割示例")
    parser.add_argument(
        "--example", "-e",
        type=int,
        default=1,
        help="选择示例 (1-8)"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="input.jpg",
        help="输入图片路径"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output.png",
        help="输出图片路径"
    )

    args = parser.parse_args()

    # 根据参数运行不同示例
    examples = {
        1: example_basic_usage,
        2: example_custom_config_file,
        3: example_override_config,
        4: example_black_background,
        5: example_custom_background_color,
        6: example_view_config,
        7: example_batch_processing,
        8: example_get_masks,
    }

    if args.example in examples:
        print(f"\n运行示例 {args.example}\n")
        examples[args.example]()
    else:
        print(f"无效的示例编号：{args.example}")
        print("可选：1-8")
