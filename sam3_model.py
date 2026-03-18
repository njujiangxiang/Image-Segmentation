"""
SAM3 模型适配器
封装 SAM (Segment Anything Model) 模型的加载和预测功能
支持配置文件加载参数
"""

import numpy as np
from typing import List, Dict, Optional
from PIL import Image
import os


class Config:
    """
    配置加载器
    从 config.ini 文件加载模型参数
    """

    DEFAULT_CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.ini"
    )

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为项目根目录的 config.ini
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置文件"""
        import configparser

        config = configparser.ConfigParser()

        if not os.path.exists(self.config_path):
            return self._get_default_config()

        config.read(self.config_path, encoding='utf-8')
        return config

    def _get_default_config(self) -> dict:
        """返回默认配置"""
        default = configparser.ConfigParser()
        default['model'] = {
            'type': 'default',
            'device': 'auto',
            'model_paths': '{}'
        }
        default['segmentation'] = {
            'default_confidence_threshold': '0.5',
            'min_mask_area_ratio': '0.01',
            'max_masks': '10',
            'multimask_output': 'false'
        }
        default['output'] = {
            'default_background_color': 'transparent',
            'default_output_format': 'png',
            'png_compression_level': '6',
            'jpeg_quality': '95',
            'save_mask': 'true',
            'mask_suffix': '_mask'
        }
        default['batch'] = {
            'batch_size': '4',
            'skip_on_error': 'true',
            'error_log': 'batch_errors.log'
        }
        default['advanced'] = {
            'enable_cache': 'false',
            'cache_dir': './cache',
            'verbose': 'false',
            'random_seed': '',
            'auto_point_optimization': 'false',
            'auto_box_optimization': 'false'
        }
        return default

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """
        获取配置值

        Args:
            section: 配置节
            key: 配置键
            fallback: 默认值

        Returns:
            配置值
        """
        try:
            value = self.config.get(section, key, fallback=fallback)
            # 去除字符串值的引号
            if value and ((value.startswith('"') and value.endswith('"')) or
                          (value.startswith("'") and value.endswith("'"))):
                value = value[1:-1]
            return value
        except Exception:
            return fallback or ""

    def get_boolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """获取布尔配置值"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except Exception:
            return fallback

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """获取整数配置值"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except Exception:
            return fallback

    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """获取浮点配置值"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except Exception:
            return fallback

    @property
    def model_type(self) -> str:
        """获取模型类型"""
        return self.get('model', 'type', 'default')

    @property
    def device(self) -> str:
        """获取设备类型"""
        return self.get('model', 'device', 'auto')

    @property
    def model_paths(self) -> dict:
        """获取模型路径映射"""
        import ast
        path_str = self.get('model', 'model_paths', '{}')
        try:
            return ast.literal_eval(path_str)
        except Exception:
            return {}

    @property
    def confidence_threshold(self) -> float:
        """获取置信度阈值"""
        return self.get_float('segmentation', 'default_confidence_threshold', 0.5)

    @property
    def min_mask_area_ratio(self) -> float:
        """获取最小掩码面积比例"""
        return self.get_float('segmentation', 'min_mask_area_ratio', 0.01)

    @property
    def max_masks(self) -> int:
        """获取最大掩码数量"""
        return self.get_int('segmentation', 'max_masks', 10)

    @property
    def multimask_output(self) -> bool:
        """获取是否多掩码输出"""
        return self.get_boolean('segmentation', 'multimask_output', False)

    @property
    def default_background_color(self) -> str:
        """获取默认背景颜色"""
        return self.get('output', 'default_background_color', 'transparent')

    @property
    def default_output_format(self) -> str:
        """获取默认输出格式"""
        return self.get('output', 'default_output_format', 'png')

    @property
    def save_mask(self) -> bool:
        """获取是否保存掩码"""
        return self.get_boolean('output', 'save_mask', True)

    @property
    def mask_suffix(self) -> str:
        """获取掩码文件名后缀"""
        return self.get('output', 'mask_suffix', '_mask')

    @property
    def batch_size(self) -> int:
        """获取批处理大小"""
        return self.get_int('batch', 'batch_size', 4)

    @property
    def skip_on_error(self) -> bool:
        """获取是否跳过错误"""
        return self.get_boolean('batch', 'skip_on_error', True)

    @property
    def verbose(self) -> bool:
        """获取是否详细日志"""
        return self.get_boolean('advanced', 'verbose', False)


class Sam3Model:
    """
    SAM3 模型包装器

    支持多种模型类型和设备选择
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        model_type: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        初始化 SAM3 模型

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
        """
        # 加载配置
        self.config = Config(config_path)

        # 配置文件值可能被传入参数覆盖
        self.model_type = model_type or self.config.model_type
        self.device = device or self._select_device(self.config.device)

        self.model = None
        self.predictor = None
        self._verbose = self.config.verbose

        self._log(f"模型类型：{self.model_type}")
        self._log(f"设备：{self.device}")

        self._load_model()

    def _log(self, message: str):
        """日志输出"""
        if self._verbose:
            print(f"[SAM3] {message}")

    def _select_device(self, device: str) -> str:
        """选择运行设备"""
        if device == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    return "cuda"
            except ImportError:
                pass
            return "cpu"
        return device

    def _load_model(self):
        """加载 SAM 模型"""
        try:
            from segment_anything import sam_model_registry, SamPredictor
            import torch

            # 获取模型路径配置
            model_paths = self.config.model_paths

            # 优先使用配置文件中指定的路径
            if self.model_type in model_paths:
                checkpoint_path = model_paths[self.model_type]
            else:
                # 使用默认路径映射
                checkpoint_map = {
                    "default": "sam_vit_b_01ec64.pth",
                    "large": "sam_vit_l_0b3195.pth",
                    "huge": "sam_vit_h_4b8939.pth"
                }
                checkpoint_path = checkpoint_map.get(
                    self.model_type,
                    checkpoint_map["default"]
                )

            self._log(f"加载模型：{checkpoint_path}")

            # 加载模型
            sam = sam_model_registry[self.model_type](checkpoint=checkpoint_path)
            sam.to(device=self.device)
            sam.eval()

            self.predictor = SamPredictor(sam)
            self._log("模型加载成功")

        except ImportError as e:
            print(f"警告：无法加载 SAM 库：{e}")
            print("请安装：pip install segment-anything")
            self.predictor = None
        except FileNotFoundError as e:
            print(f"警告：模型文件未找到：{e}")
            print("请从以下地址下载模型:")
            print("  https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth")
            self.predictor = None

    def predict(
        self,
        image: np.ndarray,
        point_coords: Optional[np.ndarray] = None,
        point_labels: Optional[np.ndarray] = None,
        box: Optional[np.ndarray] = None,
        multimask_output: Optional[bool] = None
    ) -> List[Dict]:
        """
        预测图像分割掩码

        Args:
            image: 输入图像 (H, W, 3) RGB numpy 数组
            point_coords: 可选的提示点坐标 (N, 2)
            point_labels: 可选的提示点标签 (N,)，1=前景，0=背景
            box: 可选的边界框 (4,) 或 (B, 4)
            multimask_output: 是否输出多个掩码，None 时使用配置文件设置

        Returns:
            掩码列表，每个掩码包含:
            - mask: 二值掩码数组
            - confidence: 置信度分数
            - iou: IoU 分数
        """
        if self.predictor is None:
            return []

        # 使用配置文件的多掩码设置
        if multimask_output is None:
            multimask_output = self.config.multimask_output

        # 设置图像
        self.predictor.set_image(image)

        # 执行预测
        masks, iou_preds, _ = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            box=box,
            multimask_output=multimask_output
        )

        # 整理结果
        results = []
        for mask, iou in zip(masks, iou_preds):
            results.append({
                "mask": mask.astype(np.uint8),
                "confidence": float(iou),
                "iou": float(iou)
            })

        # 按置信度排序
        results.sort(key=lambda x: x["confidence"], reverse=True)

        # 限制返回数量
        max_masks = self.config.max_masks
        if len(results) > max_masks:
            results = results[:max_masks]

        return results

    def predict_with_points(
        self,
        image: np.ndarray,
        foreground_points: List[tuple],
        background_points: Optional[List[tuple]] = None
    ) -> List[Dict]:
        """
        使用点提示进行分割

        Args:
            image: 输入图像
            foreground_points: 前景点列表 [(x1, y1), (x2, y2), ...]
            background_points: 背景点列表 (可选)

        Returns:
            掩码列表
        """
        if self.predictor is None:
            return []

        self.predictor.set_image(image)

        # 构建点坐标和标签
        points = []
        labels = []

        for x, y in foreground_points:
            points.append([x, y])
            labels.append(1)

        if background_points:
            for x, y in background_points:
                points.append([x, y])
                labels.append(0)

        point_coords = np.array(points, dtype=np.float32)
        point_labels = np.array(labels, dtype=np.int32)

        return self.predict(image, point_coords=point_coords, point_labels=point_labels)

    def predict_with_box(
        self,
        image: np.ndarray,
        box: List[int]
    ) -> List[Dict]:
        """
        使用边界框提示进行分割

        Args:
            image: 输入图像
            box: 边界框 [x1, y1, x2, y2]

        Returns:
            掩码列表
        """
        if self.predictor is None:
            return []

        self.predictor.set_image(image)
        box_array = np.array(box, dtype=np.float32)

        return self.predict(image, box=box_array)

    def get_config(self) -> Config:
        """获取配置对象"""
        return self.config


# 便捷函数
def load_sam_model(
    config_path: Optional[str] = None,
    model_type: Optional[str] = None,
    device: Optional[str] = None
) -> Sam3Model:
    """
    加载 SAM 模型的便捷函数

    Args:
        config_path: 配置文件路径
        model_type: 模型类型，覆盖配置文件设置
        device: 运行设备，覆盖配置文件设置

    Returns:
        Sam3Model 实例
    """
    return Sam3Model(
        config_path=config_path,
        model_type=model_type,
        device=device
    )


if __name__ == "__main__":
    # 测试模型加载
    print("正在加载 SAM 模型...")

    # 从配置文件加载
    model = Sam3Model(config_path="config.ini")

    if model.predictor is not None:
        print("模型加载成功!")
        print(f"设备：{model.device}")
        print(f"模型类型：{model.model_type}")
        print(f"置信度阈值：{model.config.confidence_threshold}")
        print(f"默认背景：{model.config.default_background_color}")
    else:
        print("模型加载失败，请检查安装和模型文件")
