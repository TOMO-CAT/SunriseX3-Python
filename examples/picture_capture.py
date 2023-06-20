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
    dump_helper = DumpHelper("./output/picture_capture", "picture_", ".jpeg")

    while True:
        img = camera_recorder.get_frame()
        dump_helper.dump(img)
        time.sleep(0.1)

    logger.info('Quit')


if __name__ == "__main__":
    main()
