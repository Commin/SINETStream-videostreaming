import os
import torch
import math
import numpy as np
from torchvision import transforms
from PIL import Image
import sys
import json
import argparse
import time
import csv
from datetime import datetime
from statistics import mean

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

code_url = os.path.dirname(__file__)#当前文件位置
with open(os.path.join(code_url, 'index'), 'r', encoding="utf-8") as f:   #{"labels_list": ["foggy", "night", "rainy", "snowy", "sunny"], "is_multilabel": false}
    index_map = json.loads(f.read())
labels_dict = index_map['labels_list']

sys.path.insert(0, code_url)

DEFAULT_CROP_PCT = 0.875
IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)
IMAGENET_INCEPTION_MEAN = (0.5, 0.5, 0.5)
IMAGENET_INCEPTION_STD = (0.5, 0.5, 0.5)
IMAGENET_DPN_MEAN = (124 / 255, 117 / 255, 104 / 255)
IMAGENET_DPN_STD = tuple([1 / (.0167 * 255)] * 3)
EPS = 0.00001

class ToNumpy:

    def __call__(self, pil_img):
        np_img = np.array(pil_img, dtype=np.uint8)
        if np_img.ndim < 3:
            np_img = np.expand_dims(np_img, axis=-1)

        np_img = np.rollaxis(np_img, 2)  # HWC to CHW
        return np_img


class ToTensor:

    def __init__(self, dtype=torch.float32):
        self.dtype = dtype

    def __call__(self, pil_img):
        np_img = np.array(pil_img, dtype=np.uint8)
        if np_img.ndim < 3:
            np_img = np.expand_dims(np_img, axis=-1)
        np_img = np.rollaxis(np_img, 2)  # HWC to CHW
        return torch.from_numpy(np_img).to(dtype=self.dtype)


def _pil_interp(method):
    if method == 'bicubic':
        return Image.BICUBIC
    elif method == 'lanczos':
        return Image.LANCZOS
    elif method == 'hamming':
        return Image.HAMMING
    else:
        # default bilinear, do we want to allow nearest?
        return Image.BILINEAR


def transforms_imagenet(
      img_size=224,
      crop_pct=None,
      interpolation='bilinear',
      use_prefetcher=False,
      mean=IMAGENET_DEFAULT_MEAN,
      std=IMAGENET_DEFAULT_STD):
    crop_pct = crop_pct or DEFAULT_CROP_PCT

    if isinstance(img_size, tuple):
        assert len(img_size) == 2
        if img_size[-1] == img_size[-2]:
            # fall-back to older behaviour so Resize scales to shortest edge if target is square
            scale_size = int(math.floor(img_size[0] / crop_pct))
        else:
            scale_size = tuple([int(x / crop_pct) for x in img_size])
    else:
        scale_size = int(math.floor(img_size / crop_pct))

    tfl = [
        transforms.Resize(scale_size, _pil_interp(interpolation)),
        transforms.CenterCrop(img_size),
    ]
    if use_prefetcher:
        # prefetcher and collate will handle tensor conversion and norm
        tfl += [ToNumpy()]
    else:
        tfl += [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=torch.tensor(mean),
                std=torch.tensor(std))
        ]

    return transforms.Compose(tfl)


def softmax(x):
    x = np.array(x)
    orig_shape = x.shape

    if len(x.shape) > 1:
        # Matrix
        exp_minmax = lambda x: np.exp(x - np.max(x))
        denom = lambda x: 1.0 / (np.sum(x) + EPS)
        x = np.apply_along_axis(exp_minmax, 1, x)
        denominator = np.apply_along_axis(denom, 1, x)
        if len(denominator.shape) == 1:
            denominator = denominator.reshape((denominator.shape[0], 1))
        x = x * denominator
    else:
        # Vector
        x_max = np.max(x)
        x = x - x_max
        numerator = np.exp(x)
        denominator = 1.0 / (np.sum(numerator) + EPS)
        x = numerator.dot(denominator)
    assert x.shape == orig_shape

    return x

def classify(img,ts):
    model = torch.load(os.path.join(code_url, "result.pickle"), map_location=device)
    model.to(device)
    transform = transforms_imagenet(img_size=380)
    model.eval()
    num_classes = len(labels_dict)
    labels = labels_dict
    #print(labels_dict)
    # img = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
    img = transform(img)
    img = torch.unsqueeze(img, 0)
    img = img.to(device)
    with torch.no_grad():
        img = model(img)

    img = img.to(torch.device('cpu')).detach().numpy()
    img = softmax(np.array(img))
    img = np.array(img[0])
    end_idx = -6 if num_classes >= 5 else -num_classes - 1
    top_k = img.argsort()[-1:end_idx:-1]
    label = labels[top_k[0]]
    res_dict = {"timestamp":ts, "predicted_label" :label}
    print(res_dict)
    detail_dict = {}
    for idx in top_k:
        detail_dict[labels[idx]] = float(img[idx])
    # print(detail_dict)
    res_dict.update(detail_dict)
    json_object = json.dumps(res_dict, indent = 4) 
    #print(json_object)
    str = "predicted_label:",labels[top_k[0]],"scores:",[[labels[idx], float(img[idx])] for idx in top_k]
    #print(str)
    return label, str

if __name__ == '__main__':
    #image_dir= './images/U080-000001.png'
    # --- Parse hyper-parameters  --- #
    parser = argparse.ArgumentParser(description='Hyper-parameters for GridDehazeNet')

    parser.add_argument('-data_path', help='directory for input image', default='./U080-000001.png',  type=str)
    parser.add_argument('-times', help='measure times', default=100,  type=int)
    parser.add_argument("-w", "--width", type=int, default=320, help="resize width")
    parser.add_argument("-h","--height", type=int, default=240, help="resize height")

    args = parser.parse_args()
    image_dir= args.data_path
    times = args.times
    img = Image.open(image_dir)
    img = img.resize(((args.width,args.height)))
    print("size", img.size)

    ts = datetime.now()
    
    csvfile_name = "weather_time_" + str(args.width) + "x" + str(args.height) + ts.strftime("_%Y/%m/%d_%H:%M:%S") + ".csv"
    csvfile_name = csvfile_name.replace("/","")
    csvfile_name = csvfile_name.replace(":","")
    with open(csvfile_name, 'w', newline='') as csvfile:
        fieldnames = ['frame', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(times):
            time_list = []
            wc_time = time.time()
            classify(img,str(i))
            wc_time = time.time()-wc_time
            time_list.append(wc_time)
            print('frame' + str(i) + 'time' + str(wc_time))
            writer.writerow({'frame': str(i), 'time': str(wc_time)})
            if i+1 == times:
                avg = mean(time_list)
                print("average time", avg)
                writer.writerow({'frame': "average", 'time': str(avg)})
    print("Saved", csvfile_name)
