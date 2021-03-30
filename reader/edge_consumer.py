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
from argparse import ArgumentParser

import sys
import cv2
from sinetstream import MessageReader
from sinetstream import MessageWriter


logging.basicConfig(level=logging.INFO)

def consumer(edge_service,cloud_service, width,height):
    with MessageReader(edge_service, value_type='image') as reader:
        with MessageWriter(cloud_service, value_type='image') as writer:
            for message in reader:
                if show_image(message,width,height):
                    sys.exit()
                writer.publish(message.value)

def show_image(message,width,height):
    global n_frame
    window_name = message.topic
    print("topic={message.topic} value='{message.value}'")
    image = message.value
    n_frame = n_frame +1
    print(image.shape, f"frame: {n_frame}")

    # period
    
    resized_img = cv2.resize(image,(width,height))
    cv2.imshow(window_name, resized_img)
    return cv2.waitKey(25) & 0xFF == ord("q")

def classify(image):
    cv2.imwrite("./image.jpg", image)


if __name__ == '__main__':
    global n_frame
    parser = ArgumentParser(description="SINETStream Edge Consumer")
    parser.add_argument("--edgeservice", metavar="SERVICE_NAME", required=True)
    parser.add_argument("--cloudservice", metavar="SERVICE_NAME", required=True)
    parser.add_argument("--width", type=int, default=320, help="resize width")
    parser.add_argument("--height", type=int, default=240, help="resize height")
    args = parser.parse_args()

    print(f": edgeservice={args.edgeservice}")
    print(f": cloudservice={args.cloudservice}")
    n_frame = 0
    try:
        consumer(args.edgeservice,args.cloudservice,args.width,args.height)
    except KeyboardInterrupt:
        sys.exit()
        cv2.destroyAllWindows()