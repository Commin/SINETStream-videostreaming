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

import cv2
from sinetstream import MessageWriter

logging.basicConfig(level=logging.INFO)

def producer(service, video, preview=False):
    with MessageWriter(service, value_type='image') as writer:
        image = next_frame(video)
        print(image.shape)
        
        while image is not None:

            writer.publish(image)

            if preview and show_preview(image):
                break
            image = next_frame(video)

def next_frame(video):
    global n_frame
    if not video.isOpened():
        return None
    success, frame = video.read()
    n_frame += 1
    return frame if success else None

def show_preview(image):
    cv2.imshow(args.input_video, image)

    # Hit 'q' to stop
    return cv2.waitKey(25) & 0xFF == ord("q")

def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def main(service, video, width, height, preview=False):
    global n_frame
    
    if not video.isOpened():
        print("ERROR: cannot open the file")
        sys.exit(1)
    
    n_frame = 0

    try:
        producer(service, video, width, height, preview)
    finally:
        video.release()
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

    print(": service="+ args.service)
    pipeline = None
    if args.input_video != None:
        print(": input-video="+ args.input_video)
    else:
        pipeline = gstreamer_pipeline(capture_width=args.width, capture_height=args.height, framerate=args.fps,
         flip_method=0, display_width=args.width, display_height=args.height)
        print(pipeline)
    if args.preview:
        print("Hit 'q' to stop")

    cap = cv2.VideoCapture(args.input_video) if args.input_video!=None else cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    main(args.service, cap, args.preview)
