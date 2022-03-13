"""
Hand Tracing Module
By: Murtaza Hassan
Youtube: http://www.youtube.com/c/MurtazasWorkshopRoboticsandAI
Website: https://www.murtazahassan.com/
"""
 
from cv2 import cv2
import mediapipe as mp
import time
 
 
class handDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.8, trackCon=0.6):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
 
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
 
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
 
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
 
    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            #for id, lm in enumerate(myHand.landmark):
            for lm in myHand.landmark:
                #print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([cx, cy, lm.z])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
 
        return lmList

    def findClosestHand(self, center, threshold = 1):
        handCloest = None
        handCenter = center
        if self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                cx = 0
                cy = 0
                for lm in hand.landmark:
                    cx += lm.x / 21
                    cy += lm.y / 21
                if center == None:
                    return hand, (cx, cy)
                dis = pow(cx - center[0], 2) + pow(cy - center[1], 2)
                if dis < threshold:
                    handCloest = hand
                    handCenter = (cx, cy)
                    threshold = dis
        return handCloest, handCenter

    def trackHandPosition(self, img, center, draw=True):
        lmList = []
        myHand, center = self.findClosestHand(center)
        if myHand != None:
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                x, y = int(lm.x * w), int(lm.y * h)
                lmList.append([x, y, id])
                if draw:
                    cv2.circle(img, (x, y), 5, (255, 0, 255), cv2.FILLED)
 
        return lmList, center
 
 
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(1)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])
 
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
 
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
 
        cv2.imshow("Image", img)
        cv2.waitKey(1)
 
 
if __name__ == "__main__":
    main()