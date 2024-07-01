from celery import shared_task
import os
import shutil
import gdown
import random
import numpy as np
import pandas as pd
from PIL import Image
from tqdm.auto import tqdm
from collections import Counter
from xml.etree import ElementTree
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
from io import BytesIO
import base64
import re


def plot_bboxes1(img_file: str, data: list, class_dict: dict, id_service:int, speed:float, status:str):
    """
    A function to plot the bounding boxes and their object classes onto the image.
    
    Parameters:
        img_file: str, A string containing the path to the image file.
        data: list, A list containing bounding box data in the format [class_idx, x_center, y_center, width, height].
        class_dict: dict, A dict containing the classes in the similar sequence as per sensor data classes.
    """
    # Reading the image and annot file
    image = img_file
    img_h, img_w, _ = image.shape
    
    # Calculating the bbox in Pascal VOC format
    for bbox in data:
        xmin, ymin, xmax, ymax,conf,class_idx = bbox
        if int(class_idx) != id_service: continue
        xmin = int(xmin)
        ymin = int(ymin)
        xmax = int(xmax)
        ymax = int(ymax)
        class_idx = int(class_idx)
        
        # Correcting bbox if out of image size
        xmin = max(0, xmin)  # Ensure xmin is non-negative
        ymin = max(0, ymin)  # Ensure ymin is non-negative
        xmax = min(img_w - 1, xmax)  # Ensure xmax is within image width
        ymax = min(img_h - 1, ymax)  # Ensure ymax is within image height
        
        
        # Creating the box and label for the image
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 255, 0), 2)
        cv2.putText(image, class_dict[class_idx], (xmin, 0 if ymin-10 < 0 else ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
    
    # Create a BytesIO object to store the image data in memory
    img_buffer = BytesIO()

    # Save the annotated image to the buffer in PNG format (adjust as needed)
    plt.imsave(img_buffer, image, format='png')  # Use imsave for efficiency

    # Move the pointer to the beginning of the buffer
    img_buffer.seek(0)

    # Convert the image data to base64 encoded string
    base64_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    return [base64_image, speed, status]

@shared_task
def ai_service(photo_base64, id_service):
    """
    This function return the predicted photo using the yolo model
    """
    # Loading the best weights
    model = YOLO('/Users/admin/Documents/SonNguyen/intern/ai_service_management/backend/Object_Detection_Satellite_Imagery_Yolov8_DIOR-main/runs/detect/yolov8n_epochs50_batch16/weights/best.pt')
    
    #convert input image from base64 to jpg
    image_decoded = base64.b64decode(photo_base64)
    image_buffer = BytesIO(image_decoded)
    image = Image.open(image_buffer)
    if image.format != 'JPEG':  # Assuming your model expects JPG
        image = image.convert('RGB')  # Convert to RGB (check model requirements)
        image_buffer = BytesIO()  # Create a new BytesIO object
        image.save(image_buffer, format='JPEG')  # Save to the BytesIO as JPG

    #jpeg photo
    jpeg_photo = image_buffer.getvalue()
    
    image = Image.open(BytesIO(jpeg_photo))
    image_np = np.array(image)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
        image_np = np.array(image)
    
    # Predicting the object using the yolo model
    pred_list = model.predict(source=image_np, imgsz=800, save=False, conf=0.5)
    
    class_dict_idx = {0: 'Expressway-Service-area',
    1: 'Expressway-toll-station',
    2: 'airplane',
    3: 'airport',
    4: 'baseballfield',
    5: 'basketballcourt',
    6: 'bridge',
    7: 'chimney',
    8: 'dam',
    9: 'golffield',
    10: 'groundtrackfield',
    11: 'harbor',
    12: 'overpass',
    13: 'ship',
    14: 'stadium',
    15: 'storagetank',
    16: 'tenniscourt',
    17: 'trainstation',
    18: 'vehicle',
    19: 'windmill'}
    
    speed = round(pred_list[0].speed["inference"],1)
    status =""
    if pred_list[0].boxes.data.numel() > 0:
        status = "success"
    else:
        status = "fail"
    return plot_bboxes1(image_np, pred_list[0].boxes.data, class_dict_idx,id_service, speed, status)
