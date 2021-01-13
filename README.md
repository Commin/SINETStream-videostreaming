# Video streaming with SINETStream (Kafka)

[SINETStream](https://github.com/nii-gakunin-cloud/sinetstream/blob/main/README.en.md) Github websit: https://github.com/nii-gakunin-cloud/sinetstream

## 1. Roles

* `Writer`: Jeston TX2.
* `Reader`: MacOS.
* `Broker`: docker container on MacOS or other device.

## 2. Preparation

### 2.1. Prepare Broker

#### 2.1.1. Prepare the backend system

Run the backend messaging systems (Kafka and MQTT) used by SINETStream in a Docker container.

Execute the following command in the Broker's host environment.

```console
[user00@host-broker]$ docker run -d --name broker --hostname broker \
                      -p 1883:1883 -p 9092:9092 sinetstream/tutorial:1.0.0
```

Show the status to confirm that the container has started successfully.

```console
[user00@host-broker]$ docker ps -l
CONTAINER ID        IMAGE                        COMMAND                  CREATED              STATUS              PORTS                                            NAMES
xxxxxxxxxxxx        sinetstream/tutorial:1.0.0   "/usr/local/bin/supe…"   About a minute ago   Up About a minute   0.0.0.0:1883->1883/tcp, 0.0.0.0:9092->9092/tcp   broker
```

#### 2.1.2. Add to hosts file

Add IP of `broker` to `/etc/hosts` of `reader` and `writer`.

```console
sudo vim /etc/hosts

[broker-ip] broker
```

### 2.2. Install SINETStream

Install the Python3 library of SINETStream on your environment of `Reader` and `Writer`.

```console
pip3 install sinetstream-kafka sinetstream-mqtt
pip3 install sinetstream-type-image
```

### 2.3. Prepare program and configuration file

### 2.3.1 Prepare reader program and configuration file

Below is the procedure.

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
[user01@reader]$ ss_url=https://github.com/Commin/SINETStream-videostreaming
[user01@reader]$ curl -O ${ss_url}/reader/.sinetstream_config.yml
```

Download the sample program of Reader that uses the SINETStream Python3 API from GitHub. Grant execute permission to the program.

```console
[user01@reader]$ curl -O ${ss_url}/reader/video_consumer.py
[user01@reader]$ chmod a+x video_consumer.py
```

Verify that the above procedure has been performed correctly. Make sure that the directories and files are the same as in the example below.

```console
[user01@reader]$ pwd
/home/user01/sinetstream/reader
[user01@reader]$ ls -a
.  ..  .sinetstream_config.yml  video_consumer.py
```

### 2.3.2 Prepare writer program and configuration file

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
[user01@writer]$ ss_url=https://github.com/Commin/SINETStream-videostreaming
[user01@writer]$ curl -O ${ss_url}/writer/.sinetstream_config.yml
```

Download the sample program of Reader that uses the SINETStream Python3 API from GitHub. Grant execute permission to the program.

```console
[user01@writer]$ curl -O ${ss_url}/writer/video_producer.py
[user01@writer]$ chmod a+x video_producer.py
```

Verify that the above procedure has been performed correctly. Make sure that the directories and files are the same as in the example below.

```console
[user01@writer]$ pwd
/home/user01/sinetstream/writer
[user01@writer]$ ls -a
.  ..  .sinetstream_config.yml  video_producer.py
```

## 3. Run Reader and Writer

In the terminal for `Reader`:

```console
python3 video_consumer.py -s video-kafka
```

* `-s` service name

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
