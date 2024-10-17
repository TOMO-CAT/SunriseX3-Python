from hobot_vio import libsrcampy
from common.log import logger
from common.config import config


class EncoderType:
    H264 = 1
    H265 = 2
    MJPEG = 3

    @staticmethod
    def string_to_int(value):
        mapping = {
            "H264": EncoderType.H264,
            "H265": EncoderType.H265,
            "MJPEG": EncoderType.MJPEG,
        }
        if value in mapping:
            return mapping[value]
        else:
            logger.fatal(f"Unknown encoder type '{value}'")
            os.exit(1)


class Encoder:
    def __init__(self, encoder_type):
        logger.info("Create Encoder")
        # Encoder 对象实现了对视频数据的编码压缩功能
        # https://developer.d-robotics.cc/api/v1/fileData/documents_pi/Python_Develop/python_vio.html?highlight=libsrcampy#encoder
        self.__encoder = libsrcampy.Encoder()
        self.__encoder_type = encoder_type

    def __del__(self):
        logger.info("Destory Encoder")
        self.__encoder.close()

    def encode(self, img):
        ret = self.__encoder.encode(
            video_chn=config.get('Encoder.video_chn'),
            type=EncoderType.string_to_int(self.__encoder_type),
            width=config.get('Encoder.width'),
            height=config.get('Encoder.height'),
            bits=config.get('Encoder.bits'),
        )
        if ret != 0:
            logger.fatal("Encode failed with ret '{}'".format(ret))
            os.exit(1)
        if self.__encoder.encode_file(img) != 0:
            logger.fatal("Encode file failed")
            os.exit(1)
        encoded_img = self.__encoder.get_img()
        return encoded_img
