from common.dump_helper import DumpHelper
from common.log import log_to_file, logger
from video.camera_recorder import CameraRecorder
import time
from common import signal


LOG_FILE_PATH = 'logs/picture_capture.log'


def main():
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting PictureCapture module ...')

    signal.signal_handler()
    camera_recorder = CameraRecorder()
    dump_helper = DumpHelper("./picture_capture", "picture_", ".jpeg")

    # while True:
    for _ in range(10):
        img = camera_recorder.get_frame()
        dump_helper.dump(img)
        time.sleep(0.1)

    # for _ in range(5000):
    #     camera_recorder.get_img(
    #         "output/pictures/{}.jpeg".format(time.time()))
    #     time.sleep(0.1)

    logger.info('Quit')


if __name__ == "__main__":
    main()
