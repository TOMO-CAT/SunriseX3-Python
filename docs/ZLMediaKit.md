# ZLMediaKit

## 文档

> <https://docs.zlmediakit.com/zh/>

一个基于 C++11 的高性能运营级流媒体服务框架。

## 安装

安装依赖库：

```bash
sudo apt install libssl-dev
```

源码编译：

```bash
git clone --depth 1 https://gitee.com/xia-chu/ZLMediaKit
cd ZLMediaKit/
git submodule update --init
mkdir build
cd build
cmake ..
make -j4
```

后台启动：

```bash
sudo ./release/linux/Debug/MediaServer -d &
```
