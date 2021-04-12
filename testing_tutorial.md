# Video streaming testing tutorial combined with EdgeVPN

## 1. Install and start EdgeVPN.

Install `evio` and start [EdgeVPN](https://edgevpn.io/install/) all on Raspberry Pi, edge device (arbitrary device can run EdgeVPN closer to Raspberry Pi), and Cloud VM.
For transmission delay measure, no need noise removal on cloud. AWS EC2 t2. series is enough.



## 2. Prepare Python environment and dependencies. 
    
Install SINETStream library:
    
```console
sudo pip3 install sinetstream-kafka sinetstream-mqtt
sudo pip3 install sinetstream-type-image
```

Due to `sinetstream-type-image` depending on `opencv-python`, you can preinstall lots of its dependencies and `opencv-python` to prevent error during installing.


```console
sudo apt install libavutil56 libcairo-gobject2 libgtk-3-0 libpango-1.0-0 libqt5core5a libavcodec58 libcairo2 libswscale5 libtiff5 libatk1.0-0 libavformat58 libgdk-pixbuf2.0-0 libilmbase24 libopenexr24 libpangocairo-1.0-0 libwebp6 libgl1-mesa-dev libcairo2-dev

sudo pip3 install opencv-python
```

Then, download program and configure file. 

### Prepare reader program and configuration file

Below is the procedure same on all devices.

1. Create a directory for `Reader`
2. Prepare the SINETStream configuration file
3. Prepare the `Reader` program

Create a directory and change to that directory.

```console
[user01@reader]$ mkdir -p ~/sinetstream/reader
[user01@reader]$ cd ~/sinetstream/reader
```

Prepare SINETStream configuration file. Download the configuration file prepared for this tutorial from GitHub.

```console
[user01@reader]$ ss_url=https://raw.githubusercontent.com/Commin/SINETStream-videostreaming/main
[user01@reader]$ curl -O ${ss_url}/reader/.sinetstream_config.yml
```

Download the sample program of Reader that uses the SINETStream Python3 API from GitHub. Grant execute permission to the program.

```console
[user01@reader]$ curl -O ${ss_url}/reader/consumer.py
[user01@reader]$ curl -O ${ss_url}/reader/video_consumer.py
[user01@reader]$ chmod a+x consumer.py video_consumer.py
```

* `producer.py` can only work with `consumer.py` to send/receive text message through SINETStream API.
* `rasp_video_producer.py` can work with `video_consumer.py` to send/receive video stream data through SINETStream API.

Verify that the above procedure has been performed correctly. Make sure that the directories and files are the same as in the example below.

```console
[user01@reader]$ pwd
/home/user01/sinetstream/reader
[user01@reader]$ ls -a
.  ..  .sinetstream_config.yml consumer.py video_consumer.py 
```

#### On edge terminal

Besides, you need to download another program file ``
to receive data from Raspberry Pi and send data to cloud broker intermediately.

```console
[user01@reader]$ curl -O ${ss_url}/reader/edge_consumer.py
[user01@reader]$ chmod a+x edge_consumer.py
```

* `edge_consumer.py` can work with `rasp_video_producer.py` and `video_consumer.py` to receive data from Raspberry Pi and send video stream data to cloud intermediately.


### Prepare writer program and configuration file

Below is the procedure.

1. Create a directory for `Writer`
2. Prepare the SINETStream configuration file
3. Prepare the `Writer` program

Create a directory and change to that directory.

```console
[user01@writer]$ mkdir -p ~/sinetstream/writer
[user01@writer]$ cd ~/sinetstream/writer
```

Prepare SINETStream configuration file. Download the configuration file prepared for this tutorial from GitHub.

```console
[user01@writer]$ ss_url=https://raw.githubusercontent.com/Commin/SINETStream-videostreaming/main
[user01@writer]$ curl -O ${ss_url}/writer/.sinetstream_config.yml
```

Download the sample program of Reader that uses the SINETStream Python3 API from GitHub. Grant execute permission to the program.

```console
[user01@writer]$ curl -O ${ss_url}/writer/producer.py
[user01@writer]$ curl -O ${ss_url}/writer/rasp_video_producer.py
[user01@writer]$ chmod a+x producer.py rasp_video_producer.py
```

Verify that the above procedure has been performed correctly. Make sure that the directories and files are the same as in the example below.

```console
[user01@writer]$ pwd
/home/user01/sinetstream/writer
[user01@writer]$ ls -a
.  ..  .sinetstream_config.yml producer.py video_producer.py 
```

### Add service to configure file.

Here is `edge-video-kafka` information:
```
edge-video-kafka:
    type: kafka
    brokers: "edge-broker:9092"
    topic: video-kafka
    value_type: image
```
   
Here is `cloud-video-kafka` information:
```
cloud-video-kafka:
    type: kafka
    brokers: "broker:9092"
    topic: video-kafka
    value_type: image
```

Add service `edge-video-kafka` and `cloud-video-kafka` information to `sinetstream/reader/.sinetstream_config.yml` and `sinetstream/writer/.sinetstream_config.yml` on Raspberry Pi.

Add service `edge-video-kafka` and `cloud-video-kafka` information to `sinetstream/reader/.sinetstream_config.yml` on edge device.

Add service `cloud-video-kafka` information to `sinetstream/reader/.sinetstream_config.yml` on cloud instance.

## 3. Start broker container.

### Prepare Broker container

Run the backend messaging systems (Kafka and MQTT) used by SINETStream in a Docker container.

Execute the following command in cloud instance.

```console
[user00@host-broker]$ docker run -d --name broker --hostname broker \
                      -p 1883:1883 -p 9092:9092 sinetstream/tutorial:latest
```

Show the status to confirm that the container has started successfully.

```console
[user00@host-broker]$ docker ps -l
CONTAINER ID        IMAGE                        COMMAND                  CREATED              STATUS              PORTS                                            NAMES
xxxxxxxxxxxx        sinetstream/tutorial:latest  "/usr/local/bin/supe…"   About a minute ago   Up About a minute   0.0.0.0:1883->1883/tcp, 0.0.0.0:9092->9092/tcp   broker
```

Change hostname to `edge-broker` and run edge `broker` container on edge device (same device as `edge-consumer.py` is OK).

```console
[user00@host-broker]$ docker run -d --name broker --hostname edge-broker \
                      -p 1883:1883 -p 9092:9092 sinetstream/tutorial:latest
```

## 4. Add IPs to hosts file

On Raspberry Pi:

Add IP of `broker`, `edge-broker`  to `/etc/hosts`.

```console
sudo vim /etc/hosts

[broker-ip] broker
[edge-broker-ip] edge-broker
```

On Edge:

Add IP of `broker` to `/etc/hosts`.

```console
sudo vim /etc/hosts

[broker-ip] broker
```

## 5. Evaluate transmission latency

Evaluate transmission latency (not including weather classification & image processing) with / without EdgeVPN (Need editing IPs in /etc/hosts file).

Variables:
Three video solutions: 240p, 360p, 480p
Three pre-set fps: 60p, 30p, 20p
Three transmission routes:
1. Rasp -  Edge - Rasp
2. Rasp -  Cloud - Rasp
3. Rasp -  Edge - Cloud - Rasp

First, run `video_consumer.py` on Raspberry Pi

For instance, for Rasp - Edge - Cloud - Rasp route, you can run `video_consumer.py` as follows:

```console
sudo python3 video_consumer.py -s edge-video-kafka --csv ./csv/edge_cloud_reader.csv
```

Second, run `edge_consumer.py` on edge terminal **(only need for the third routes)**

you can run `edge_consumer.py` as follows:

```console
sudo python3 edge_consumer.py --edgeservice edge-video-kafka --cloudservice cloud-video-kafka
```

Third, run `exp_rasp_video_producer.py` on Raspberry Pi (for Round-trip time)

you can run `exp_rasp_video_producer.py` as follows:

```console
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 426 --height 240 --fps 60 --csv ./csv/rasp_edge_cloud_rasp_240p_60fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 426 --height 240 --fps 30 --csv ./csv/rasp_edge_cloud_rasp_240p_30fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 426 --height 240 --fps 20 --csv ./csv/rasp_edge_cloud_rasp_240p_20fps.csv --frame 100

sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 640 --height 360 --fps 60 --csv ./csv/rasp_edge_cloud_rasp_360p_60fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 640 --height 360 --fps 30 --csv ./csv/rasp_edge_cloud_rasp_360p_30fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 640 --height 360 --fps 20 --csv ./csv/rasp_edge_cloud_rasp_360p_20fps.csv --frame 100

sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 854 --height 480 --fps 60 --csv ./csv/rasp_edge_cloud_rasp_480p_60fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 854 --height 480 --fps 30 --csv ./csv/rasp_edge_cloud_rasp_480p_30fps.csv --frame 100
sudo python3 exp_rasp_video_producer.py -s edge-video-kafka --width 854 --height 480 --fps 20 --csv ./csv/rasp_edge_cloud_rasp_480p_20fps.csv --frame 100
```

For the first & second routes, please edit `--csv` parameters correspondingly.
Particularly, for the second route: Rasp -  Cloud - Rasp, please edit `-s` parameter to `cloud-video-kafka`.

Finally, list all data from .csv file and calculate average latency (RTT) for all conditions.
