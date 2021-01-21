#!/usr/bin/env python3

# Copyright (C) 2020 National Institute of Informatics
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import logging
import argparse
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

import cv2
from sinetstream import MessageWriter

logging.basicConfig(level=logging.INFO)

def producer(service, video, preview=False):
    global n_frame
    with MessageWriter(service, value_type='image') as writer:

        # capture frames from the camera
        for frame in camera.capture_continuous(video, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            image = frame.array
            n_frame += 1
            print( f"frame: {n_frame}")
            writer.publish(image)
            # show the frame
            if preview and show_preview(image):
                break

            # clear the stream in preparation for the next frame
            video.truncate(0)

def show_preview(image):
    cv2.imshow(args.input_video, image)

    # Hit 'q' to stop
    return cv2.waitKey(25) & 0xFF == ord("q")



def main(service, video, preview=False):
    global n_frame

    n_frame = 0

    try:
        producer(service, video, preview)
    finally:
        print("Fin video (#frame="+str(n_frame)+")")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="SINETStream Producer")
    parser.add_argument("-s", "--service", metavar="SERVICE_NAME", required=True)
    parser.add_argument("-f", "--input-video", metavar="FILE")
    parser.add_argument("-c", "--camera", type=int, default=0)
    parser.add_argument("-p", "--preview", action="store_true", help="show on local too")
    parser.add_argument("--width", type=int, default=320, help="resize width")
    parser.add_argument("--height", type=int, default=240, help="resize height")
    parser.add_argument("--fps", type=int, default=30, help="set video fps")
    
    args = parser.parse_args()

    camera = PiCamera()

    print(": service="+ args.service)
    pipeline = None
    if args.input_video != None:
        print(": input-video="+ args.input_video)
    else:
        # initialize the camera and grab a reference to the raw camera capture
        camera.resolution = (args.width, args.height)
        camera.framerate = args.fps
        rawCapture = PiRGBArray(camera, size=(args.width, args.height))
        # allow the camera to warmup
        time.sleep(0.1)
    if args.preview:
        print("Hit 'q' to stop")

    main(args.service, rawCapture, args.preview)
