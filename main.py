from hobot_vio import libsrcampy
import time

cam = libsrcampy.Camera()
ret = cam.open_cam(0, 1, 30, 1920, 1080)
print("Camera open_cam return:%d" % ret)
# wait for isp tuning
time.sleep(1)
img = cam.get_img(2)
if img is not None:
    # save file
    fo = open("output.img", "wb")
    fo.write(img)
    fo.close()
    print("camera save img file success")
else:
    print("camera save img file failed")
cam.close_cam()
print("test_camera done!!!")

# encode file
enc = libsrcampy.Encoder()
ret = enc.encode(0, 1, 1920, 1080)
print("Encoder encode return:%d" % ret)

# save file
fo = open("encode.h264", "wb+")
a = 0
fin = open("output.img", "rb")
input_img = fin.read()
fin.close()
while a < 100:
    ret = enc.encode_file(input_img)
    print("Encoder encode_file return:%d" % ret)
    img = enc.get_img()
    if img is not None:
        fo.write(img)
        print("encode write image success count: %d" % a)
    else:
        print("encode write image failed count: %d" % a)
    a = a + 1

enc.close()
print("test_encode done!!!")

# decode start
dec = libsrcampy.Decoder()

ret = dec.decode("encode.h264", 0, 1, 1920, 1080)
print("Decoder return:%d frame count: %d" % (ret[0], ret[1]))

img = dec.get_img()
if img is not None:
    # save file
    fo = open("output.img", "wb")
    fo.write(img)
    fo.close()
    print("decode save img file success")
else:
    print("decode save img file failed")

dec.close()
print("test_decode done!!!")
