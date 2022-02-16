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
from customize_service import classify
import sys
from cv2 import imshow, waitKey, resize
from sinetstream import MessageReader


logging.basicConfig(level=logging.INFO)

def consumer(service,width,height,interval):
    with MessageReader(service, value_type='image') as reader:
        for message in reader:
            if show_image(message,width,height,interval):
                sys.exit()

def show_image(message,width,height,interval):
    global n_frame
    #window_name = message.topic
    print("topic={message.topic} value='{message.value}'")
    image = message.value
    if n_frame % interval == 0:
        classify(image)

    n_frame = n_frame +1
    print(image.shape, f"frame: {n_frame}")
    
    #cv2.imwrite("./image.jpg", image)
    #resized_img = resize(image,(width,height))
    
    #imshow(window_name, resized_img)
    return waitKey(25) & 0xFF == ord("q")

if __name__ == '__main__':
    global n_frame
    parser = ArgumentParser(description="SINETStream Consumer")
    parser.add_argument("-s", "--service", metavar="SERVICE_NAME", required=True)
    parser.add_argument("--width", type=int, default=320, help="resize width")
    parser.add_argument("--height", type=int, default=240, help="resize height")
    parser.add_argument("--interval", type=int, default=10, help="classify weather per which frames")
    args = parser.parse_args()

    print(f": service={args.service}")
    n_frame = 0
    try:
        consumer(args.service, args.width, args.height, args.interval)
    except KeyboardInterrupt:
        sys.exit()
