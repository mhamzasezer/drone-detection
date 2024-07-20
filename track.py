import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import cv2
import numpy as np
from reolinkapi import Camera
from simple_pid import PID
import time

# Camera's IP, username, and password
camera_ip = '192.168.0.52'
username = 'admin'
password = '6540pachinko'

# Initialize the camera
camera = Camera(ip=camera_ip, username=username, password=password)

# Capture video stream
video_url = f'rtsp://{username}:{password}@{camera_ip}//h264Preview_01_main'
cap = cv2.VideoCapture(video_url)

# Retry mechanism for video capture initialization
if not cap.isOpened():
    cv2.waitKey(1000)  # Wait for 1 second and try again
    cap.open(video_url)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

# Make the display window resizable
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

# Define the lower and upper bounds of the red color in HSV space
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Initialize PID controllers for pan and tilt
pan_pid = PID(0.1, 0.01, 0.005, setpoint=0)  # Tune these values as needed
tilt_pid = PID(0.1, 0.01, 0.005, setpoint=0)  # Tune these values as needed

# Define the region of interest (ROI) as a percentage of the frame size
roi_x_percent = 0.5  # 50% width
roi_y_percent = 0.5  # 50% height

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            continue

        # Convert frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Apply the red color masks
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour and its bounding box
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 1000:  # Example size threshold, adjust as needed
                x, y, w, h = cv2.boundingRect(largest_contour)
                cX, cY = x + w // 2, y + h // 2

                # Draw the bounding box and centroid on the frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                cv2.putText(frame, "center", (cX - 20, cY - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # Calculate the center of the video frame
                frame_center_x, frame_center_y = frame.shape[1] // 2, frame.shape[0] // 2

                # Define the ROI boundaries
                roi_left = int(frame_center_x - (frame.shape[1] * roi_x_percent / 2))
                roi_right = int(frame_center_x + (frame.shape[1] * roi_x_percent / 2))
                roi_top = int(frame_center_y - (frame.shape[0] * roi_y_percent / 2))
                roi_bottom = int(frame_center_y + (frame.shape[0] * roi_y_percent / 2))

                # Draw the ROI on the frame
                cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)

                # Calculate the offset from the center
                offset_x = cX - frame_center_x
                offset_y = cY - frame_center_y

                # Adjust the PID setpoints
                pan_pid.setpoint = 0
                tilt_pid.setpoint = 0

                # Get the control values from the PID controllers
                pan_control = pan_pid(offset_x)
                tilt_control = tilt_pid(offset_y)

                # Determine the direction to move based on the control values
                if abs(offset_x) > frame.shape[1] * roi_x_percent / 2:
                    if offset_x < 0:
                        print("Moving left")
                        camera.move_left()
                    else:
                        print("Moving right")
                        camera.move_right()

                if abs(offset_y) > frame.shape[0] * roi_y_percent / 2:
                    if offset_y < 0:
                        print("Moving up")
                        camera.move_up()
                    else:
                        print("Moving down")
                        camera.move_down()

                time.sleep(0.05)  # Reduce time for camera to move and update

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
 
 