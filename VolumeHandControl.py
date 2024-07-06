import cv2  # Import OpenCV library for image processing
import time  # Import time library to measure FPS
import numpy as np  # Import numpy library for numerical operations
import HandTrackingModule as htm  # Import custom hand tracking module
import math  # Import math library for mathematical operations
from ctypes import cast, POINTER  # Import necessary functions from ctypes for audio control
from comtypes import CLSCTX_ALL  # Import CLSCTX_ALL from comtypes for audio control
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # Import pycaw for audio control

wCam, hCam = 640, 480  # Set the width and height of the webcam feed

# Initialize video capture from the default camera (use 0 for the default camera)
cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # Set the width of the camera
cap.set(4, hCam)  # Set the height of the camera
pTime = 0  # Initialize previous time for FPS calculation

# Create a handDetector object with a detection confidence of 0.7
detector = htm.handDetector(detectionCon=0.7)

# Get the audio device for controlling volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range for the audio device
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()  # Capture a frame from the camera
    if not success:
        continue  # If frame capture failed, skip this iteration

    img = detector.findHands(img)  # Detect hands and draw landmarks on the image
    lmList = detector.findPosition(img, draw=False)  # Get the positions of landmarks

    if len(lmList) != 0:
        # Get the coordinates of the thumb tip and the index finger tip
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw circles on the thumb tip and the index finger tip
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # Draw a line between the two points
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # Draw a circle at the midpoint

        # Calculate the length between the two points
        length = math.hypot(x2 - x1, y2 - y1)

        # Map the length to volume range
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)  # Set the system volume based on the calculated volume level

        # Change the color of the midpoint circle if the distance is less than 50
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Draw the volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 255), 3)  # Changed to pink color
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 255), cv2.FILLED)  # Changed to pink color
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 255), 3)  # Changed to pink color and updated font style

    # Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (40, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)  # Removed "FPS" label, changed to pink color and updated font style

    # Display the image
    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Wait for 1 ms and check if 'q' is pressed
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
