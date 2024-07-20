import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import cv2
import requests
from reolinkapi import Camera


# Replace with your camera's IP, username, and password
camera_ip = '192.168.0.52'
username = 'admin'
password = '6540pachinko'

# Initialize the camera
camera = Camera(ip=camera_ip, username=username, password=password)

# Print available methods
print(dir(camera))
