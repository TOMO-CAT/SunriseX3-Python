
from common.log import log_to_file, logger
from video.camera_recorder import CameraRecorder
import time


LOG_FILE_PATH = 'logs/video_capture.log'


def main():
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting VideoCapture module ...')

    camera_recorder = CameraRecorder()
    for i in range(100):
        camera_recorder.get_img(f"output/output{i}.jpeg")
        time.sleep(1)

    logger.info('Quit')


if __name__ == "__main__":
    main()
