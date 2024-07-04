import cv2  # Import OpenCV library for image processing
import mediapipe as mp  # Import MediaPipe library for hand tracking
import time  # Import time library to measure FPS

# Initialize video capture from the default camera (index 1)
cap = cv2.VideoCapture(1)

# Initialize MediaPipe Hands solution
mpHands = mp.solutions.hands
hands = mpHands.Hands()  # Create a Hands object for hand tracking
mpDraw = mp.solutions.drawing_utils  # Utility for drawing hand landmarks

# Initialize variables to calculate FPS
pTime = 0  # Previous time
cTime = 0  # Current time

while True:
    success, img = cap.read()  # Capture a frame from the camera
    if not success:
        continue  # Skip the iteration if frame capture failed

    # Convert the BGR image to RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the RGB image to find hand landmarks
    results = hands.process(imgRGB)

    # Check if any hand landmarks were detected
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:  # Loop through each detected hand
            for id, lm in enumerate(handLms.landmark):  # Loop through each landmark
                # Get the image dimensions
                h, w, c = img.shape
                # Calculate the pixel coordinates of the landmark
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)  # Print the landmark ID and its coordinates
                # Draw a circle on the landmark
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            # Draw the hand landmarks on the image
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Calculate the frames per second (FPS)
    cTime = time.time()  # Get the current time
    fps = 1 / (cTime - pTime)  # Calculate FPS
    pTime = cTime  # Update the previous time

    # Display the FPS on the image
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 255), 3)

    # Display the image
    cv2.imshow("Image", img)
    cv2.waitKey(1)  # Wait for 1 ms before moving to the next frame
