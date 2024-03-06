import datetime
import logging
import pathlib
from typing import Optional, Dict, List, Tuple

import cv2
import numpy as np
from omegaconf import DictConfig

from .common import Face, FacePartsName, Visualizer
from .gaze_estimator import GazeEstimator
from .utils import get_3d_face_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoForFlask:
    """
    为了适应flask构建app，参照Demo做一些修改，
    包括不再使用opencv绘制任何信息，将gaze_vector返回等等
    这个对象在构建app时就创建，前端有图片传过来就执行run的动作 -> 这边暂时只考虑图片
    """
    def __init__(self, config: DictConfig):
        self.config = config
        self.gaze_estimator = GazeEstimator(config)  # 初始化模型
        self.face_model_3d = get_3d_face_model(config)
        self.camera = self.gaze_estimator.camera   # 需要它来投影

    def run(self, image) -> List[Dict]:
        """
        对图片做预测，返回偏转角度、gaze_vector等信息
        todo: 这边image应该是bgr
        """
        return self._process_image(image)

    def _process_image(self, image) -> List[Dict]:
        gaze_infos: List[Dict] = []
        undistorted = cv2.undistort(
            image, self.gaze_estimator.camera.camera_matrix,
            self.gaze_estimator.camera.dist_coefficients)

        faces = self.gaze_estimator.detect_faces(undistorted)
        for face in faces:
            self.gaze_estimator.estimate_gaze(undistorted, face)
            try:
                gaze_info = self._get_gaze_info(face)
            except:
                gaze_info = None
            if gaze_info:
                gaze_infos.append(gaze_info)
        return gaze_infos

    @staticmethod
    def _convert_pt(point: np.ndarray) -> Tuple[int, int]:
        return tuple(np.round(point).astype(np.int).tolist())

    def _get_gaze_info(self, face: Face) -> Dict:
        length = self.config.demo.gaze_visualization_length
        if self.config.mode == 'MPIIGaze':
            # 此处为了方便，暂时不实现
            raise NotImplementedError
        elif self.config.mode in ['MPIIFaceGaze', 'ETH-XGaze']:
            point0 = face.center
            point1 = face.center + length * face.gaze_vector

            # 3d点投影成2d点
            assert point0.shape == point1.shape == (3,)
            points3d = np.vstack([point0, point1])
            points2d = self.camera.project_points(points3d)
            pt0 = self._convert_pt(points2d[0])
            pt1 = self._convert_pt(points2d[1])
            pitch, yaw = np.rad2deg(face.vector_to_angle(face.gaze_vector))

            return {"gaze_origin2d": pt0, "gaze_point2d": pt1, "pitch": pitch, "yaw": yaw}

        else:
            raise ValueError


