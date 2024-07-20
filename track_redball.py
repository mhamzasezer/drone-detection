import urllib3
import cv2
import numpy as np
from reolinkapi import Camera
from simple_pid import PID
from time import time, sleep
import os

# Disable warnings from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Environment variables for credentials and camera IP
camera_ip = os.getenv('CAMERA_IP', '')
username = os.getenv('CAMERA_USERNAME', 'admin')
password = os.getenv('CAMERA_PASSWORD', '')

# Initialize the camera
camera = Camera(ip=camera_ip, username=username, password=password)

# Capture video stream
video_url = f'rtsp://{username}:{password}@{camera_ip}//h264Preview_01_main'
cap = cv2.VideoCapture(video_url)

# Retry mechanism for video capture initialization
retry_attempts = 5
for attempt in range(retry_attempts):
    if cap.isOpened():
        break
    print(f"Attempt {attempt+1} of {retry_attempts}: Could not open video stream. Retrying...")
    sleep(2**attempt)  # Exponential backoff
else:
    print("Error: Could not open video stream after multiple attempts.")
    exit()

# Make the display window resizable
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

# Define the lower and upper bounds of the red color in HSV space
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Initialize PID controllers for pan and tilt with more dynamic adjustments
pan_pid = PID(0.1, 0.01, 0.005, setpoint=0)
tilt_pid = PID(0.1, 0.01, 0.005, setpoint=0)

# Define the region of interest (ROI) as a percentage of the frame size
roi_x_percent = 0.5  # 50% width
roi_y_percent = 0.5  # 50% height

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 1000:
                x, y, w, h = cv2.boundingRect(largest_contour)
                cX, cY = x + w // 2, y + h // 2

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

                frame_center_x, frame_center_y = frame.shape[1] // 2, frame.shape[0] // 2

                offset_x = cX - frame_center_x
                offset_y = cY - frame_center_y

                pan_control = pan_pid(offset_x)
                tilt_control = tilt_pid(offset_y)

                # Adjust camera movement based on PID control values
                if abs(pan_control) > 1:  # Threshold can be adjusted
                    if pan_control < 0:
                        camera.move_left()
                    else:
                        camera.move_right()

                if abs(tilt_control) > 1:  # Threshold can be adjusted
                    if tilt_control < 0:
                        camera.move_up()
                    else:
                        camera.move_down()

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    
