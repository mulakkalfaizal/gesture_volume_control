import cv2
import time
import numpy as np
import handTrackingModule as htm
import math
import osascript

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)

pTime = 0
cTime = 0

minVol = 0
maxVol = 100

vol = 0
volBar = 400
volPer = 0

detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        # Get the x,y coordinates of the thump finger tip and index finger tip
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        # Get the center point of the finger tips
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw a circle on the x,y coordinates of the finger.
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Draw a line between the finger tips
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 4)

        # Find the length of the line (tip of both the fingers)
        length = math.hypot(x2 - x1, y2 - y1)
        #print(f"Length: {length}")

        # Convert the length between finger tip proportional to the laptop volume value [0, 100]
        vol = np.interp(length, [50, 150], [minVol, maxVol])
        print(f"Length: {length} => Volume converted : {vol}")

        # Convert the length between finger tip proportional to the volume bar rectangle spec
        volBar = np.interp(length, [50, 150], [400, 150])

        # Convert teh length between finger tip to percentage
        volPer = np.interp(length, [50, 150], [0, 100])

        # Change the volume of the laptop with osascript
        osascript.osascript(f"set volume output volume {vol}")

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    """
    Draw the volume control bar
    (50, 150) represents the top left corner of rectangle
    (85, 400) represents the bottom right corner of rectangle
    """
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)

    """
    Draw the volume bar inside the above rectangle
    (50, int(volBar) represent how much the rectangle should go up 
    (85, 400) is the same as the outer rectangle which we draw before
    """
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)

    # show the volume percentage near the volume bar (40, 450) is the coordinates where text should be shown
    cv2.putText(img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # Add the frame per second to the vedio
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
