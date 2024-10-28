from common.log import log_to_file, logger
from video.camera import Camera
from video.encoder import Encoder
from common import signal
import time
import librtmp

LOG_FILE_PATH = 'logs/publish_rtmp_stream.log'
RTMP_URL = 'rtmp://127.0.0.1/live/0'


def main():
    # -c:v copy 避免转码，提高推流速度
    #
    # 手动 ffmpeg 推流到 rtmp: ffmpeg -re -i test_data/4361065-uhd_3840_2160_25fps.mp4 -c:v copy -f flv 'rtmp://127.0.0.1/live/0'
    #
    # 循环播放: ffmpeg -stream_loop -100 -i test_data/4361065-uhd_3840_2160_25fps.mp4 -c:v copy -f flv 'rtmp://127.0.0.1/live/0'

    # sudo python3 -m examples.publish_rtmp_stream
    log_to_file(LOG_FILE_PATH)
    logger.info('Starting PublishRtmpStream module ...')

    signal.signal_handler()
    camera = Camera()
    encoder = Encoder("H264")

    rtmp_conn = librtmp.RTMP(RTMP_URL)
    logger.info('Start connect to rtmp server...')
    rtmp_conn.connect()
    logger.info('Connect to rtmp server successfully!')

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
