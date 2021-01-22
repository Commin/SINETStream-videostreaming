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
from sys import exit

import cv2
from sinetstream import MessageWriter

logging.basicConfig(level=logging.INFO)


def producer(service, image, preview=False):
    with MessageWriter(service, value_type='image') as writer:
        writer.publish(image)
        print(image.shape)
        if preview:
            show_preview(image)


def show_preview(image):
    cv2.imshow(args.input_image, image)

    # Hit 'q' to stop
    return cv2.waitKey(25) & 0xFF == ord("q")


if __name__ == '__main__':

    parser = ArgumentParser(description="SINETStream Producer")
    parser.add_argument("-s", "--service", metavar="SERVICE_NAME", required=True)
    parser.add_argument("-f", "--input-image", metavar="FILE", required=True)
    parser.add_argument("-p", "--preview", action="store_true", help="show on local too")
    parser.add_argument("--width", type=int, default=320, help="resize width")
    parser.add_argument("--height", type=int, default=240, help="resize height")
    args = parser.parse_args()

    print(f": service={args.service}")
    print(f": input-image={args.input_image}")
    if args.preview:
        print("Hit 'q' to stop")

    try:
        dim = (args.width, args.height)
        image = cv2.imread(args.input_image)
        image = cv2.resize(image, dim)
        producer(args.service, image, args.preview)
    finally:
        print(f"Published {args.input_image}")