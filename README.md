# Video streaming with SINETStream (Kafka)

[SINETStream](https://github.com/nii-gakunin-cloud/sinetstream/blob/main/README.en.md) Github websit: https://github.com/nii-gakunin-cloud/sinetstream
[Testing tutorial](https://github.com/Commin/SINETStream-videostreaming/blob/main/testing_tutorial.md): video streaming from Raspberry Pi to edge & cloud server with SINETStream combined with [EdgeVPN](https://edgevpn.io/).

## 1. Introduction

* `Writer`: Jeston TX2, Raspberry Pi.
* `Reader`: MacOS.
* `Broker`: docker container on MacOS or other device.

Camera on Jeston TX2 can capture video stream, and publish each frame with SINETStream through broker to MacOS (of course, other device is OK) as Reader.

## introduction of writer side program

`video_producer.py` as `Writer` on Jeston TX2.

`producer` class:

```Python
def producer(service, video, preview=False):
    with MessageWriter(service, value_type='image') as writer:
        image = next_frame(video)
        print(image.shape)
        
        while image is not None:
            writer.publish(image)
            if preview and show_preview(image):
                break
            image = next_frame(video)
```

In the mode of video stream from camera, Jeston TX2 can use `gstreamer` to open its onboard or USB camera, and use `cv2` library to capture the video stream. 

```Python
# open its onboard or USB camera with parameters
pipeline = gstreamer_pipeline(capture_width=args.width, capture_height=args.height, framerate=args.fps, flip_method=0,
    display_width=args.width, display_height=args.height)
# capture the video stream from camera, and finally input to producer class
cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
```

## introduction of reader side program

`video_consumer.py` as `Reader` on MacOS (or other devices).

`consumer` class:

```Python
def consumer(service):
    with MessageReader(service, value_type='image') as reader:
        for message in reader:
            if show_image(message):
                sys.exit()
```

As the reader side, user only needs to define service name same as the `Writer`. `MessageReader` can subscribe each frame as message, and show each frame of video with function `show_image(message)`.

[Here](#jump) for details of input parameters.

## 2. Producer and Consumer program

<span id="jump">Details for input parameters</span>

In the terminal for `Reader`:

```console
python3 video_consumer.py -s video-kafka
```

* `-s` service name

For Jestson TX2, you can run `video_producer.py`.
In the terminal for `Writer`:

```console
python3 video_producer.py -s video-kafka -c 0 -p
```

* `-s` service name (same as `Reader` program)
* `-c` webcam source id (usually 0)
* `-p` show preview locally (optional)
* `--width` resize video width (default value: 320)
* `--height` resize video height (default value: 240)
* `--fps` set video frame rate (default value: 30)

For Raspberry Pi, you can run `rasp_video_producer.py`.
In the terminal for `Writer`:

```console
python3 rasp_video_producer.py -s video-kafka
```

* `-s` service name (same as `Reader` program)
* `-p` show preview locally (optional)
* `--width` resize video width (default value: 320)
* `--height` resize video height (default value: 240)
* `--fps` set video frame rate (default value: 30)
