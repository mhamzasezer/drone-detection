import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import cv2
import requests
from reolinkapi import Camera


# Replace with your camera's IP, username, and password
camera_ip = ''
username = 'admin'
password = ''

# Initialize the camera
camera = Camera(ip=camera_ip, username=username, password=password)

# Print available methods
print(dir(camera))
