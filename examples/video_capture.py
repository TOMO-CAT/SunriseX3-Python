
from common.log import log_to_file, logger
from video.camera_recorder import CameraRecorder
import time
from common import signal


LOG_FILE_PATH = 'logs/video_capture.log'


def main():
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting VideoCapture module ...')

    signal.signal_handler()

    camera_recorder = CameraRecorder()
    for _ in range(5000):
        camera_recorder.get_img(
            "output/pictures/{}.jpeg".format(time.time()))
        time.sleep(0.1)

    logger.info('Quit')


if __name__ == "__main__":
    main()
