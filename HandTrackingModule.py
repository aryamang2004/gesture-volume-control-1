import cv2  # Import OpenCV library for image processing
import mediapipe as mp  # Import MediaPipe library for hand tracking
import time  # Import time library to measure FPS

# Define a class for hand detection
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        # Initialize the handDetector class with default parameters
        self.mode = mode  # Mode for hands detection (static image mode or video mode)
        self.maxHands = maxHands  # Maximum number of hands to detect
        self.detectionCon = detectionCon  # Minimum detection confidence threshold
        self.trackCon = trackCon  # Minimum tracking confidence threshold
        
        # Initialize MediaPipe Hands solution
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils  # Utility for drawing hand landmarks

    def findHands(self, img, draw=True):
        # Check if the image is valid
        if img is None or img.size == 0:
            return img  # Return immediately if the image is empty
        
        # Convert the BGR image to RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the RGB image to find hand landmarks
        self.results = self.hands.process(imgRGB)
        
        # Check if any hand landmarks were detected
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:  # Loop through each detected hand
                if draw:
                    # Draw the hand landmarks on the image
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []  # List to store the positions of landmarks
        
        # Check if any hand landmarks were detected
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]  # Get the specified hand
            for id, lm in enumerate(myHand.landmark):  # Loop through each landmark
                # Get the image dimensions
                h, w, c = img.shape
                # Calculate the pixel coordinates of the landmark
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])  # Append the landmark ID and its coordinates to the list
                if draw:
                    # Draw a smaller circle on the landmark
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList

def main():
    # Initialize variables to calculate FPS
    pTime = 0  # Previous time
    cTime = 0  # Current time
    
    # Initialize video capture from the default camera (index 0)
    cap = cv2.VideoCapture(0)  # Try different indices: 0, 1, 2, etc.
    
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video device")
        return

    # Create an object of the handDetector class
    detector = handDetector()
    
    while True:
        success, img = cap.read()  # Capture a frame from the camera
        if not success or img is None:
            print("Failed to capture image")
            continue

        img = detector.findHands(img)  # Detect hands and draw landmarks
        lmList = detector.findPosition(img)  # Get the positions of landmarks
        if len(lmList) != 0:
            print(lmList[4])  # Print the position of the fifth landmark (index 4)

        # Calculate the frames per second (FPS)
        cTime = time.time()  # Get the current time
        fps = 1 / (cTime - pTime)  # Calculate FPS
        pTime = cTime  # Update the previous time

        # Display the FPS on the image
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        
        # Display the image
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Wait for 1 ms and check if 'q' is pressed
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()  # Run the main function
