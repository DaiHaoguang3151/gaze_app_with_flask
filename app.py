import base64
from typing import List, Dict

import cv2
import numpy as np

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

from init_model import init_model_from_args, DemoForFlask

app = Flask(__name__)
app.secret_key = 'whatever'
socketio = SocketIO(app)

# 点击的点的id
POINT_IDs = ["top_left", "top_right", "bottom_right", "bottom_left"]


def init_gaze_estimation_model() -> DemoForFlask:
    """
    在构建app时，初始化模型
    """
    return init_model_from_args()


gaze_model_for_flask = init_gaze_estimation_model()


@app.before_request
def before_request():
    """
    每次刷新页面，都要设置一些全局变量
    """
    # 有效的点击的点的id
    session["valid_clicked_point_ids"] = []
    # 用于记录点击的点对用的视线角度
    session["gaze_infos_of_clicked_points"] = {}
    # 角度范围
    session["bound_angles"] = {}
    # 四个点对应的gaze_vector
    session["bound_vectors2d"] = {}


def gaze_estimation(image_data) -> List[Dict]:
    """
    根据前端传来的image_data，使用gaze_model预测gaze_vector
    """
    img = np.asarray(bytearray(image_data), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return gaze_model_for_flask.run(img)


@app.route('/')
def index():
    """
    这个测试页面是一个前置的用于相机标定的页面，
    点击四个角点，获取人眼在观测屏幕的角度偏转范围
    """
    return render_template('index.html')


@socketio.on('image')
def handle_image(data):
    # gaze estimation
    encoded_data = data.split(',')[1]
    image_data = base64.b64decode(encoded_data)
    gaze_infos = gaze_estimation(image_data)
    # dummy
    # gaze_infos = [{"pitch": 20, "yaw": 28, "gaze_origin2d": [20, 200], "gaze_point2d": [50, 250]}]
    emit('gaze_result', {'result': gaze_infos,
                         'bound_angles': session["bound_angles"],
                         'bounding_box': calculate_gaze_bounding_box(gaze_infos)})


def calculate_gaze_bounding_box(gaze_infos: List[Dict]) -> List[List]:
    """
    根据面部中心以及之前获取的四个角点的gaze_vector2d计算处每次的视角包围盒
    """
    assert len(session["bound_vectors2d"]) == len(POINT_IDs), "点的个数不正确"

    points2d = []
    if not gaze_infos:
        return points2d
    # 默认只选第一个视线
    gaze_info = gaze_infos[0]

    for point_id in POINT_IDs:
        vec = session["bound_vectors2d"][point_id]
        points2d.append((np.array(vec) + np.array(gaze_info["gaze_origin2d"])).tolist())

    return points2d


@socketio.on('point_and_image')
def handle_point_and_image(data):
    """
    在点击前端的点之后，获取点的id，并且处理截图数据，获得对应的视线角度
    """
    # 模拟后端执行视线检测逻辑
    if not data.get("point_id") or not data.get("image"):
        # todo:前端警告
        print("请重新点击")
        return

    if data["point_id"] in session.get("valid_clicked_point_ids"):
        # 更新状态
        pass
    else:
        session["valid_clicked_point_ids"].append(data["point_id"])

    # gaze estimation
    encoded_data = data["image"].split(',')[1]
    image_data = base64.b64decode(encoded_data)
    gaze_infos = gaze_estimation(image_data)

    emit('point_and_image_status',
         {
             'point_id': data['point_id'],
             'gaze_infos': gaze_infos,
             'status': 'success'
         },
         broadcast=False   # todo: 只传给触发事件的客户端，不能用广播
         )
    # 保存每一次的角度
    session["gaze_infos_of_clicked_points"].update({data['point_id']: gaze_infos})

    if sorted(session["valid_clicked_point_ids"]) == sorted(POINT_IDs):
        emit('start_estimation', broadcast=False)
        print("gaze_infos_of_clicked_points: ", session["valid_clicked_point_ids"])

        # # dummy
        # gaze_infos_of_clicked_points = {'top_left': [{"pitch": 30, "yaw": -30}],
        #                             'top_right': [{"pitch": 30, "yaw": 30}],
        #                             'bottom_right': [{"pitch": -30, "yaw": 30}],
        #                             'bottom_left': [{"pitch": -30, "yaw": -30}]}

        # 计算bound angles todo: 优化
        pitch_list = sorted([gaze_infos[0]["pitch"] for gaze_infos in session["gaze_infos_of_clicked_points"].values()])
        yaw_list = sorted([gaze_infos[0]["yaw"] for gaze_infos in session["gaze_infos_of_clicked_points"].values()])
        min_pitch, max_pitch = pitch_list[0], pitch_list[-1]
        min_yaw, max_yaw = yaw_list[0], yaw_list[-1]
        session["bound_angles"] = {"pitch": [min_pitch, max_pitch], "yaw": [min_yaw, max_yaw]}

        # 计算bound vectors
        for point_id in POINT_IDs:   # 保持顺时针连接
            gaze_info = session["gaze_infos_of_clicked_points"][point_id][0]
            gaze_vector2d = (np.array(gaze_info["gaze_point2d"]) - np.array(gaze_info["gaze_origin2d"])).tolist()
            session["bound_vectors2d"].update({point_id: gaze_vector2d})


if __name__ == '__main__':
    # socketio.run(app, debug=True, keyfile="key.pem", certfile="cert.pem")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, keyfile="key.pem", certfile="cert.pem")
    # socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
