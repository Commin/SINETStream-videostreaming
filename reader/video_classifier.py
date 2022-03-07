from argparse import ArgumentParser
import cv2
import numpy as np
from PIL import Image
from sinetstream import MessageReader
from sinetstream import MessageWriter
from multiprocessing import Process, Queue, freeze_support
from queue import Empty
from datetime import datetime
from customize_service import classify
from logging import getLogger

import csv
import time

def arg_parse():
    parser = ArgumentParser(description="SINETStream Consumer")
    parser.add_argument("-ss", "--subservice",  metavar="SERVICE_NAME", default="cloud-video-kafka")
    parser.add_argument("-ws", "--weaservice", default="weather-kafka")
    parser.add_argument("--width", type=int, default=320, help="resize width")
    parser.add_argument("--height", type=int, default=240, help="resize height")
    parser.add_argument("--interval", type=int, default=10, help="classify weather per which frames")
    return parser.parse_args()

logger = getLogger(__name__)

video_que = Queue(1)
res_que = Queue(1)
weather_que = Queue(1)

def consumer(v, w, sub_service, interval):
    frame = 0
    with MessageReader(sub_service,value_type='image') as reader:
        reader.seek_to_end()
        for msg in reader:
            #print("topic={msg.topic} value='{msg.value}'")
            v.put(msg)
            if frame % interval == 0:
                w.put(msg)
            frame += 1


def producer(v, r):
    frame = 0
    pub_service = "sunny-video-kafka"
    while True:
        with MessageWriter(pub_service,value_type='image') as writer:
            print("service={pub_service}\n")
            while True:
                try:
                    video = v.get(True,0.1).value
                    writer.publish(video)
                    frame += 1
                    print('Published %d frames' % (frame))
                    res = r.get(True,0.1)
                    if res not in pub_service:
                        pub_service = res + "-video-kafka"
                        break
                except Empty:
                    pass
                cv2.waitKey(1)


def classifier(r, wea_service):
    frame = 0
    with MessageWriter(wea_service,value_type='text') as writer:
        while True:
            try:
                msg = r.get(True,0.1)
                print(msg)
                print(type(msg))
                writer.publish(msg)
                
                print('Published %d frames' % (frame))
                frame += 1
            except Empty:
                pass
            cv2.waitKey(1)

def classify_frame(sub_que, res_que):
    frame = 0

    while True:
        try:
            msg = sub_que.get(True, 0.1)
            ts = datetime.fromtimestamp(msg.timestamp)            
            image = msg.value
            img = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
            label, res = classify(img,ts.strftime("%Y/%m/%d, %H:%M:%S"))
            frame += 1
            if label == "night":
                label = "sunny"
            res_que.put(label)
        except Empty:
            pass
        except Exception:
            logger.exception(
                f"{msg.topic}(offset={msg.raw.offset}): Incorrect format")
        cv2.waitKey(1)



if __name__ == '__main__':
    args = arg_parse()
    
    freeze_support()
    Process(target=consumer, args=(video_que, weather_que, args.subservice, args.interval), daemon=True).start()
    Process(target=classifier, args=(res_que, args.weaservice), daemon= True).start()
    Process(target=producer, args=(video_que, res_que), daemon= True).start()
    classify_frame(weather_que, res_que)
    
    
