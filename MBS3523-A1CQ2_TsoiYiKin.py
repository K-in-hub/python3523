import cv2
import numpy as np
import serial
import time

arduino = serial.Serial('COM5', 9600)
time.sleep(2)

cap = cv2.VideoCapture(0)
width = 640
height = 480

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(largest_contour)

        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            cv2.circle(frame, (cx, cy), 7, (255, 0, 255), -1)

            errorPan = cx - (width / 2)
            errorTilt = cy - (height / 2)

            if abs(errorPan) > 100:
                if errorPan > 0:
                    arduino.write(b'L')
                else:
                    arduino.write(b'R')
            else:
                arduino.write(b'S')

            if abs(errorTilt) > 100:
                if errorTilt > 0:
                    arduino.write(b'U')
                else:
                    arduino.write(b'D')
            else:
                arduino.write(b'S')

        else:
            arduino.write(b'S')

    else:
        arduino.write(b'S')

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
