from common.log import logger
from hobot_vio import libsrcampy
import os
from time import sleep


def sensor_reset_shell():
    os.system("echo 19 > /sys/class/gpio/export")
    os.system("echo out > /sys/class/gpio/gpio19/direction")
    os.system("echo 0 > /sys/class/gpio/gpio19/value")
    sleep(0.2)
    os.system("echo 1 > /sys/class/gpio/gpio19/value")
    os.system("echo 19 > /sys/class/gpio/unexport")
    os.system("echo 1 > /sys/class/vps/mipi_host0/param/stop_check_instart")


class CameraRecorder(object):
    def __init__(self):
        logger.info("Creating CameraRecorder")
        sensor_reset_shell()

        # Camera 对象用于完成 MIPI Camera 的图像采集和处理功能
        # https://developer.d-robotics.cc/api/v1/fileData/documents_pi/Python_Develop/python_vio.html?highlight=libsrcampy#camera
        self._camera = libsrcampy.Camera()
        if self._camera.open_cam(pipe_id=0, video_index=1, fps=30, width=1920, height=1080) != 0:
            logger.fatal('Open camera fail')
            os.exit(1)
        # 等待摄像头参数校正, 否则画面失真(偏蓝偏黑)
        # sleep(1)

        # Encoder 对象实现了对视频数据的编码压缩功能
        # https://developer.d-robotics.cc/api/v1/fileData/documents_pi/Python_Develop/python_vio.html?highlight=libsrcampy#encoder
        self._encoder = libsrcampy.Encoder()

    def __del__(self):
        logger.info("Destory CameraRecorder")
        # self._decoder.close()c
        self._encoder.close()
        self._camera.close_cam()

    def get_img(self, out_img_path):
        file_dir = os.path.dirname(out_img_path)
        if not os.path.exists(file_dir):
            logger.warning(
                'Folder [{}] does not exist, creating to dump logs'.format(file_dir))
            os.makedirs(file_dir)

        img = self._camera.get_img(module=2, width=1920, height=1080)
        if img is None:
            logger.fatal("Get img from camera failed")
        # encode_type: 1(H264) 2(H265) 3(MJPEG)
        ret = self._encoder.encode(video_chn=0, type=3,
                                   width=1920, height=1080, bits=80000)
        if ret != 0:
            logger.fatal("Encode failed with ret '{}'".format(ret))
        if self._encoder.encode_file(img) != 0:
            logger.fatal("Encode file failed")
        encoded_img = self._encoder.get_img()
        if encoded_img is None:
            logger.fatal("Get image from encoder fail")
        with open(out_img_path, "wb+") as f:
            f.write(encoded_img)
        logger.info(f"Get image '{out_img_path}' success")

    def get_frame(self):
        img = self._camera.get_img(module=2, width=1920, height=1080)
        if img is None:
            logger.fatal("Get img from camera failed")
        # encode_type: 1(H264) 2(H265) 3(MJPEG)
        ret = self._encoder.encode(video_chn=0, type=3,
                                   width=1920, height=1080, bits=80000)
        if ret != 0:
            logger.fatal("Encode failed with ret '{}'".format(ret))
        if self._encoder.encode_file(img) != 0:
            logger.fatal("Encode file failed")
        encoded_img = self._encoder.get_img()
        if encoded_img is None:
            logger.fatal("Get image from encoder fail")
        return encoded_img
