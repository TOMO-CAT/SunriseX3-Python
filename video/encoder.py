from hobot_vio import libsrcampy
from common.log import logger


class Encoder:
    def __init__(self):
        logger.info("Create Encoder")
        # Encoder 对象实现了对视频数据的编码压缩功能
        # https://developer.d-robotics.cc/api/v1/fileData/documents_pi/Python_Develop/python_vio.html?highlight=libsrcampy#encoder
        self.__encoder = libsrcampy.Encoder()

    def __del__(self):
        logger.info("Destory Encoder")
        self.__encoder.close()

    def encode(self, img):
        ret = self.__encoder.encode(video_chn=0, type=3,
                                    width=1920, height=1080, bits=80000)
        if ret != 0:
            logger.fatal("Encode failed with ret '{}'".format(ret))
            os.exit(1)
        if self.__encoder.encode_file(img) != 0:
            logger.fatal("Encode file failed")
            os.exit(1)
        encoded_img = self.__encoder.get_img()
        return encoded_img
