# TestData

## 测试用的 mp4 文件

> <https://mirror.aarnet.edu.au/pub/TED-talks/>
> <https://www.pexels.com/search/videos/demo/>

## 剔除音频

```bash
ffmpeg -i test_data/4361065-uhd_3840_2160_25fps.mp4 -an -c:v copy -f mp4 test_data/4361065-uhd_3840_2160_25fps_without_audio.mp4
```

## 查看视频信息

```bash
ffprobe test_data/4361065-uhd_3840_2160_25fps.mp4
```
