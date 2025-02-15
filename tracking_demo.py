import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import cv2
import numpy as np
import time

# Camera's IP, username, and password
camera_ip = ''
username = 'admin'
password = ''

# Initialize the camera
video_url = f'rtsp://{username}:{password}@{camera_ip}//h264Preview_01_main'
cap = cv2.VideoCapture(video_url)

# Retry mechanism for video capture initialization
# if not cap.isOpened():
#     cv2.waitKey(1000)  # Wait for 1 second and try again
#     cap.open(video_url)
#     if not cap.isOpened():
#         print("Error: Could not open video stream.")
#         exit()

# Make the display window resizable
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

# Define the lower and upper bounds of the red color in HSV space
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

frame_skip = 3  # Process every 3nd frame

try:
    while True:
        # start_time = time.time()

        # Skip frames
        for _ in range(frame_skip):
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                continue

        # Resize frame for faster processing
        frame = cv2.resize(frame, (640, 480))

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

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # end_time = time.time()
        # print(f"Frame processing time: {end_time - start_time:.2f} seconds")

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

