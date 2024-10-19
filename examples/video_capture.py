from common.log import log_to_file, logger
from video.camera import Camera
from video.encoder import Encoder
from common import signal
import time
import cv2

LOG_FILE_PATH = 'logs/video_capture.log'
OUTPUT_VIDEO_FILE_PATH = 'output/video_capture.264'


def main():
    # sudo python3 -m examples.video_capture
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting VideoCapture module ...')

    signal.signal_handler()
    camera = Camera()
    encoder = Encoder("H264")

    fo = open(OUTPUT_VIDEO_FILE_PATH, "wb+")

    for i in range(50):
        raw_img = camera.get_raw_img()
        img = encoder.encode(raw_img)
        if img is not None:
            fo.write(img)
            logger.info(f"write image success count {i}")
        else:
            logger.error(f"write image failed count {i}")
        fo.write(img)
        i += 1
        time.sleep(1)

    logger.info('Quit')


if __name__ == "__main__":
    main()
