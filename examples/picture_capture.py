from common.log import log_to_file, logger
from video.camera import Camera
from video.encoder import Encoder
from common.dump_helper import DumpHelper
import time
from common import signal


LOG_FILE_PATH = 'logs/picture_capture.log'


def main():
    # sudo python3 -m examples.picture_capture
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting VideoCapture module ...')

    signal.signal_handler()

    camera = Camera()
    encoder = Encoder("MJPEG")
    dump_helper = DumpHelper("./output/picture_capture", "picture_", ".jpeg")

    for _ in range(500):
        raw_img = camera.get_raw_img()
        img = encoder.encode(raw_img)
        dump_helper.dump(img)
        time.sleep(0.5)

    logger.info('Quit')


if __name__ == "__main__":
    main()
