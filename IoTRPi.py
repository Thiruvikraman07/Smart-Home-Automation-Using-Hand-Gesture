import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('/Users/thiruanand/PycharmProjects/IoTMiniProject/iot-test-project-fe291-firebase-adminsdk-wgkgn-e621255274.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://iot-test-project-fe291-default-rtdb.asia-southeast1.firebasedatabase.app"
})

led_status_ref = db.reference('/led/status')

led_inten_ref = db.reference('/led/intensity')


import cv2
import time
import math
import osascript
import numpy as np
from HandTrackingModule import handDetector

led_status = False
closed_start_time = 0
open_start_time = 0
stable_percentage = 0
stable_timer = 0
prevol = 0
closed_start_time_vol=0
vol = 0
volBar = 0
def check_fist_status(hand_landmarks):
    if hand_landmarks[8][2] < hand_landmarks[5][2] and hand_landmarks[12][2] < hand_landmarks[9][2] and hand_landmarks[16][2] < hand_landmarks[13][2] and hand_landmarks[20][2] < hand_landmarks[17][2]:
        return "Open"
    else:
        return "Closed"

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    global led_status
    global closed_start_time
    global open_start_time
    global stable_percentage
    global stable_timer
    global prevol
    global closed_start_time_vol
    global vol
    global volBar

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            fist_status = check_fist_status(lmList)
            cv2.putText(img, fist_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            current_time = time.time()

            if fist_status == "Closed":
                if closed_start_time == 0:
                    closed_start_time = current_time
                elif current_time - closed_start_time >= 5:
                    led_status = False

            else:
                if open_start_time == 0:
                    open_start_time = current_time
                elif current_time - open_start_time >= 5:
                    led_status = True

            if fist_status == "Closed":
                open_start_time = 0
            else:
                closed_start_time = 0

            if led_status:
                lmlist = lmList
                x1, y1 = lmlist[4][1], lmlist[4][2]
                x2, y2 = lmlist[8][1], lmlist[8][2]

                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)

                vol = np.interp(length, [30, 300], [0, 100])
                volBar = np.interp(length, [30, 300], [400, 150])

                if prevol-2 <= vol and vol <= prevol+2:
                    if closed_start_time_vol == 0:
                        closed_start_time_vol = current_time
                    elif current_time - closed_start_time_vol >= 10:
                        stable_percentage = vol



                if length < 50:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

                prevol = vol

                led_inten_ref.set(stable_percentage)

        if led_status:
            a = "LED STATUS: ON"
            led_status_ref.set('on')
        else:
            a = "LED STATUS: OFF"
            led_status_ref.set('off')

        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(vol)) + " %", (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        cv2.putText(img, "FIXED: " + str(int(stable_percentage)) + " %", (40, 490), cv2.FONT_HERSHEY_PLAIN, 3,(0, 255, 0), 3)
        cv2.putText(img, a, (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
