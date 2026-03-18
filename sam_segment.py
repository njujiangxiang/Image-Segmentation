"""
SAM 图像分割工具
基于 SAM (Segment Anything Model) 实现图像主体分割和背景替换
支持配置文件加载参数
"""

import numpy as np
from PIL import Image
from typing import Optional, Tuple, Union
from sam3_model import Sam3Model, Config


class SAMImageSegmenter:
    """
    SAM 图像分割器

    功能:
    - 自动识别并分割图像主体
    - 去除背景，支持自定义填充颜色
    - 支持多种输出格式
    - 支持配置文件加载参数
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        model_type: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        初始化分割器

        Args:
            config_path: 配置文件路径，默认使用 config.ini
            model_type: 模型类型，覆盖配置文件设置
                - 'default': 默认模型 (ViT-B)
                - 'large': 大型模型 (ViT-L)
                - 'huge': 超大型模型 (ViT-H)
            device: 运行设备，覆盖配置文件设置
                - 'auto': 自动选择 (优先 CUDA)
                - 'cuda': 使用 GPU
                - 'cpu': 使用 CPU

        示例:
            >>> # 使用配置文件默认设置
            >>> segmenter = SAMImageSegmenter()

            >>> # 使用自定义配置文件
            >>> segmenter = SAMImageSegmenter(config_path="./my_config.ini")

            >>> # 覆盖配置文件设置
            >>> segmenter = SAMImageSegmenter(
            ...     config_path="./config.ini",
            ...     model_type="large",
            ...     device="cuda"
            ... )
        """
        # 加载配置
        self.config = Config(config_path)

        # 初始化模型（配置文件值可被参数覆盖）
        self.model = Sam3Model(
            config_path=config_path,
            model_type=model_type,
            device=device
        )

        # 获取输出配置
        self._save_mask = self.config.save_mask
        self._mask_suffix = self.config.mask_suffix

    def segment(
        self,
        input_path: str,
        output_path: str,
        background_color: Optional[Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
        output_format: Optional[str] = None,
        confidence_threshold: Optional[float] = None
    ) -> dict:
        """
        分割图像并保存结果

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            background_color: 背景颜色
                - None: 使用配置文件默认值
                - "transparent": 透明背景
                - "black": 黑色背景
                - "white": 白色背景
                - RGB 元组：(R, G, B) 如 (0, 0, 0)
                - RGBA 元组：(R, G, B, A) 如 (0, 0, 0, 255)
            output_format: 输出格式，'png', 'jpg', 'webp'
            confidence_threshold: 置信度阈值 (0-1)

        Returns:
            处理结果字典，包含：
            - success: 是否成功
            - output_path: 输出路径
            - mask_path: 掩码图路径 (可选)
            - confidence: 置信度分数
            - message: 状态信息

        示例:
            >>> segmenter = SAMImageSegmenter()
            >>> result = segmenter.segment(
            ...     input_path="input.jpg",
            ...     output_path="output.png",
            ...     background_color="black"
            ... )
            >>> if result["success"]:
            ...     print(f"输出：{result['output_path']}")
        """
        try:
            # 使用配置文件默认值
            if background_color is None:
                background_color = self.config.default_background_color
            if output_format is None:
                output_format = self.config.default_output_format
            if confidence_threshold is None:
                confidence_threshold = self.config.confidence_threshold

            # 加载图像
            image = Image.open(input_path).convert("RGB")
            image_array = np.array(image)

            # 使用 SAM 模型生成分割掩码
            masks = self.model.predict(image_array)

            # 选择最佳掩码（置信度最高的）
            best_mask = None
            best_confidence = 0

            for mask_info in masks:
                if mask_info["confidence"] > best_confidence:
                    best_confidence = mask_info["confidence"]
                    best_mask = mask_info["mask"]

            if best_mask is None or best_confidence < confidence_threshold:
                return {
                    "success": False,
                    "message": f"未找到满足置信度要求的分割区域 (threshold={confidence_threshold})"
                }

            # 应用置信度阈值
            binary_mask = (best_mask > confidence_threshold).astype(np.uint8) * 255

            # 处理背景颜色
            result_image = self._apply_background_color(
                image, binary_mask, background_color
            )

            # 保存结果
            if output_format.lower() == "jpg" and background_color == "transparent":
                # JPEG 不支持透明，自动改为白色背景
                result_image = self._apply_background_color(
                    image, binary_mask, "white"
                )
                output_path = output_path.replace(".png", ".jpg")

            # 保存设置
            save_params = {}
            if output_format.lower() == "png":
                save_params["compress_level"] = self.config.get_int(
                    'output', 'png_compression_level', 6
                )
            elif output_format.lower() == "jpg":
                save_params["quality"] = self.config.get_int(
                    'output', 'jpeg_quality', 95
                )

            result_image.save(output_path, **save_params)

            # 保存掩码图
            mask_path = None
            if self._save_mask:
                mask_path = (
                    output_path.rsplit(".", 1)[0] +
                    self._mask_suffix + ".png"
                )
                mask_image = Image.fromarray(binary_mask, mode="L")
                mask_image.save(mask_path)

            return {
                "success": True,
                "output_path": output_path,
                "mask_path": mask_path,
                "confidence": float(best_confidence),
                "message": "图像分割完成"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"处理失败：{str(e)}"
            }

    def _apply_background_color(
        self,
        image: Image.Image,
        mask: np.ndarray,
        background_color: Union[str, Tuple]
    ) -> Image.Image:
        """
        应用背景颜色

        Args:
            image: 原始图像
            mask: 二值掩码
            background_color: 背景颜色

        Returns:
            处理后的图像
        """
        # 创建 RGBA 图像
        rgba_image = image.convert("RGBA")
        mask_image = Image.fromarray(mask, mode="L")

        # 解析背景颜色
        if isinstance(background_color, str):
            if background_color == "transparent":
                # 透明背景
                rgba_image.putalpha(mask_image)
                return rgba_image
            elif background_color == "black":
                bg_color = (0, 0, 0, 255)
            elif background_color == "white":
                bg_color = (255, 255, 255, 255)
            else:
                bg_color = (0, 0, 0, 255)  # 默认黑色
        elif isinstance(background_color, tuple):
            if len(background_color) == 3:
                bg_color = (*background_color, 255)
            elif len(background_color) == 4:
                bg_color = background_color
            else:
                bg_color = (0, 0, 0, 255)
        else:
            bg_color = (0, 0, 0, 255)

        # 创建背景图像
        bg_image = Image.new("RGBA", image.size, bg_color)

        # 使用掩码合成
        bg_image.paste(rgba_image, mask=mask_image)

        return bg_image

    def get_masks(
        self,
        input_path: str,
        return_all: bool = False
    ) -> list:
        """
        获取图像的所有分割掩码

        Args:
            input_path: 输入图片路径
            return_all: 是否返回所有掩码，否则只返回最佳掩码

        Returns:
            掩码列表，每个掩码包含 mask 和 confidence
        """
        image = Image.open(input_path).convert("RGB")
        image_array = np.array(image)

        masks = self.model.predict(image_array)

        if return_all:
            return masks
        else:
            # 返回置信度最高的掩码
            if masks:
                best_mask = max(masks, key=lambda x: x["confidence"])
                return [best_mask]
            return []

    def segment_batch(
        self,
        input_paths: list,
        output_dir: str,
        background_color: Optional[Union[str, Tuple]] = None,
        confidence_threshold: Optional[float] = None,
        **kwargs
    ) -> list:
        """
        批量处理图像

        Args:
            input_paths: 输入图片路径列表
            output_dir: 输出目录
            background_color: 背景颜色，默认使用配置文件设置
            confidence_threshold: 置信度阈值，默认使用配置文件设置
            **kwargs: 其他参数传递给 segment 方法

        Returns:
            处理结果列表

        示例:
            >>> segmenter = SAMImageSegmenter()
            >>> results = segmenter.segment_batch(
            ...     input_paths=["img1.jpg", "img2.jpg", "img3.jpg"],
            ...     output_dir="output",
            ...     background_color="white"
            ... )
        """
        import os
        import logging

        # 配置日志
        if self.config.verbose:
            logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        os.makedirs(output_dir, exist_ok=True)

        results = []
        error_log = []

        # 使用配置文件的批处理设置
        skip_on_error = self.config.skip_on_error

        for input_path in input_paths:
            try:
                filename = os.path.basename(input_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(
                    output_dir,
                    f"{name}_no_bg.png"
                )

                result = self.segment(
                    input_path=input_path,
                    output_path=output_path,
                    background_color=background_color,
                    confidence_threshold=confidence_threshold,
                    **kwargs
                )
                results.append(result)

                if not result["success"]:
                    error_log.append(
                        f"{input_path}: {result['message']}"
                    )
                    logger.warning(
                        f"处理失败 {input_path}: {result['message']}"
                    )

            except Exception as e:
                error_log.append(f"{input_path}: {str(e)}")
                logger.error(f"处理异常 {input_path}: {str(e)}")

                if not skip_on_error:
                    raise

        # 写入错误日志
        if error_log and self.config.verbose:
            error_log_path = os.path.join(
                output_dir,
                self.config.get('batch', 'error_log', 'batch_errors.log')
            )
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(error_log))

        return results

    def get_config(self) -> Config:
        """获取配置对象"""
        return self.config


def create_segmenter(
    config_path: Optional[str] = None,
    model_type: Optional[str] = None,
    device: Optional[str] = None
) -> SAMImageSegmenter:
    """
    创建分割器实例的便捷函数

    Args:
        config_path: 配置文件路径
        model_type: 模型类型，覆盖配置文件设置
        device: 运行设备，覆盖配置文件设置

    Returns:
        SAMImageSegmenter 实例

    示例:
        >>> # 使用配置文件默认设置
        >>> segmenter = create_segmenter()

        >>> # 使用高性能配置
        >>> segmenter = create_segmenter(
        ...     model_type="large",
        ...     device="cuda"
        ... )
    """
    return SAMImageSegmenter(
        config_path=config_path,
        model_type=model_type,
        device=device
    )


if __name__ == "__main__":
    # 简单的命令行测试
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="SAM 图像分割工具"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="输入图片路径"
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="输出图片路径"
    )
    parser.add_argument(
        "--background", "-b",
        default=None,
        help="背景颜色 (transparent/black/white 或 RGB 值)"
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="配置文件路径"
    )
    parser.add_argument(
        "--model-type", "-m",
        default=None,
        choices=["default", "large", "huge"],
        help="模型类型"
    )
    parser.add_argument(
        "--device", "-d",
        default=None,
        choices=["auto", "cuda", "cpu"],
        help="运行设备"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=None,
        help="置信度阈值 (0-1)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 无参数时显示帮助
    if args.input is None:
        parser.print_help()
        print("\n示例:")
        print("  python sam_segment.py input.jpg")
        print("  python sam_segment.py input.jpg output.png")
        print("  python sam_segment.py input.jpg -b black")
        print("  python sam_segment.py input.jpg -c config.ini -m large -d cuda")
        sys.exit(0)

    # 创建分割器
    segmenter = create_segmenter(
        config_path=args.config,
        model_type=args.model_type,
        device=args.device
    )

    # 显示配置信息
    if args.verbose or segmenter.config.verbose:
        config = segmenter.get_config()
        print("=" * 40)
        print("配置信息:")
        print(f"  模型类型：{config.model_type}")
        print(f"  设备：{segmenter.model.device}")
        print(f"  置信度阈值：{config.confidence_threshold}")
        print(f"  默认背景：{config.default_background_color}")
        print("=" * 40)

    # 执行分割
    output_file = args.output or "output_no_bg.png"
    bg_color = args.background

    result = segmenter.segment(
        input_path=args.input,
        output_path=output_file,
        background_color=bg_color,
        confidence_threshold=args.threshold
    )

    if result["success"]:
        print(f"成功！输出：{result['output_path']}")
        if result.get("mask_path"):
            print(f"掩码：{result['mask_path']}")
        print(f"置信度：{result['confidence']:.2%}")
    else:
        print(f"失败：{result['message']}")
        sys.exit(1)
