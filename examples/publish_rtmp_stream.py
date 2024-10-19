from common.log import log_to_file, logger
from video.camera import Camera
from video.encoder import Encoder
from common import signal
import time
import librtmp

LOG_FILE_PATH = 'logs/publish_rtmp_stream.log'
RTMP_URL = 'rtmp://127.0.0.1/live/stream'


def main():
    # sudo python3 -m examples.publish_rtmp_stream
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting PublishRtmpStream module ...')

    signal.signal_handler()
    camera = Camera()
    encoder = Encoder("H264")

    rtmp_conn = librtmp.RTMP(RTMP_URL)
    rtmp_conn.connect()

    rtmp_stream = rtmp_conn.create_stream()
    rtmp_conn.publish(rtmp_stream)

    i = 0
    while True:
        i += 1
        raw_img = camera.get_raw_img()
        img = encoder.encode(raw_img)
        if img is not None:
            fo.write(img)
            logger.info(f"write image success count {i}")
        else:
            logger.error(f"write image failed count {i}")
        rtmp_conn.write(rtmp_stream, img)

    conn.close()


if __name__ == "__main__":
    main()
