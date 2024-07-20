# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import cv2
import requests
from reolinkapi import Camera

# Replace with your camera's IP, username, and password
camera_ip = '192.168.0.52'
username = 'admin'
password = '6540pachinko'

try:
    # Initialize the camera
    camera = Camera(ip=camera_ip, username=username, password=password)
    
    # Move the camera to a specific position (example: pan to the right)
    camera.move_right(speed=1)

    # Capture video stream
    video_url = f'rtsp://{username}:{password}@{camera_ip}//h264Preview_01_main'
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('Reolink PTZ Camera', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except KeyboardInterrupt:
    print("Interrupted! Stopping the camera movement...")
    camera.stop_ptz()  # Ensure to send a stop command
    cap.release()
    cv2.destroyAllWindows()

except requests.exceptions.RequestException as e:
    print(f"Error communicating with the camera: {e}")
except requests.exceptions.JSONDecodeError as e:
    print(f"Error decoding JSON response from the camera: {e}")
except AttributeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    # Ensure resources are released properly
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    camera.stop_ptz()  # Ensure to send a stop command
