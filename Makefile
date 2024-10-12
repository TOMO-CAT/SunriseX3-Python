.PHONY: all

all:
	sudo python3 -B -m examples.video_capture

clear:
	rm -rf output
	rm -rf logs
