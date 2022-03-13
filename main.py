from cv2 import cv2
import time
import sys
import HandTrackingModule as htm
import win32api, win32con

CLICK_DELAY = 0.5
STOP_RANGE = 7
FINGER_THRESHOLD = [1.5, 1.6, 1.4, 1]

def pointDistance(p1, p2):
    return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)

def powDistance(list, p1, p2):
    return pow(list[p1][0] - list[p2][0], 2) + pow(list[p1][1] - list[p2][1], 2)

def getFingerState(list):
    baseDis = powDistance(list, 0, 5)
    dis = [powDistance(list, 0, 8), 
           powDistance(list, 0, 12), 
           powDistance(list, 0, 16), 
           powDistance(list, 0, 20)]
    fingerState = []
    for i in range(0, 4):
        if baseDis * FINGER_THRESHOLD[i] * 2 < dis[i]: # finger pointing
            fingerState.append(1)
        elif baseDis * FINGER_THRESHOLD[i] > dis[i]: # finger closing
            fingerState.append(-1)
        else:
            fingerState.append(0)
    return fingerState

        
'''def callback(recognizer, audio):
    try:
        print("detecting")
        text = r.recognize_google(audio)
        print("you said: " + text)
        if text == "hey":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            time.sleep(.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            print("click")
        return text

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return 1

    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return -1'''

def main(argv):
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    detector = htm.handDetector()
    #r = sr.Recognizer()
    #mic = sr.Microphone()

    screen = (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
    canvas = (cap.get(3), cap.get(4))
    rate = (screen[0] *1.5 / canvas[0], screen[1]*1.5 / canvas[1]) # TODO : * z
    prevFingerLoc = (0, 0)

    bufferIndex = 0
    bufferSize = 3
    bufferX = [0] * bufferSize
    bufferY = [0] * bufferSize

    stopTime = 0
    fingerTime = 0
    fingerState = []
    isMouseDown = False

    #with mic as source:
    #    r.adjust_for_ambient_noise(source)
    #stop_listening = r.listen_in_background(mic, callback)

    isShow = not "-h" in argv
    while True:
        cTime = time.time()
        frameTime = (cTime - pTime)
        #fps = 1 / frameTime
        pTime = cTime

        success, img = cap.read()
        img = detector.findHands(img, draw=isShow)
        lmList = detector.findPosition(img, draw=isShow)
        action = "none"

        if len(lmList) != 0:
            fs = getFingerState(lmList)
            if fs != fingerState:
                fingerState = fs
                fingerTime = 0
                stopTime = 0
            else:
                fingerTime += frameTime

            if fs == [1, -1, -1, -1] or fs == [1, 1, -1, -1] or fs == [1, 1, 1, 1]:
                cursor = (((canvas[0] - lmList[8][0]) * rate[0]), lmList[8][1] * rate[1])
                cursor = (int(cursor[0] * 1.5 - screen[0] * 0.05), int(cursor[1] * 1.5 - screen[1] * 0.05))
                bufferX[bufferIndex] = cursor[0]
                bufferY[bufferIndex] = cursor[1]
                bufferIndex = (bufferIndex + 1) % bufferSize

                avgCursor = (sum(bufferX) // bufferSize, sum(bufferY) // bufferSize)
                win32api.SetCursorPos(avgCursor)

                if fingerTime != 0 and abs(avgCursor[0] - cursor[0]) < STOP_RANGE and abs(avgCursor[1] - cursor[1]) < STOP_RANGE:
                    stopTime += frameTime
                else:
                    stopTime = 0
            
            if fs == [1, 1, 1, -1] or fs == [1, 1, 1, 0]:
                '''if lmList[8][0] < lmList[16][0]:
                    action = "wheel_up"
                else:
                    action = "wheel_down"'''
                action = "wheel"
                wheel_distance = lmList[8][1] - prevFingerLoc[1]
            elif stopTime - frameTime < CLICK_DELAY and stopTime > CLICK_DELAY:
                if fs == [1, -1, -1, -1]:
                    action = "mouse_click"
                elif fs == [1, 1, -1, -1] and not isMouseDown:
                    action = "mouse_down"
                    isMouseDown = True
            elif isMouseDown and fingerTime == 0:
                action = "mouse_up"
                isMouseDown = False
            elif fs == [1, -1, -1, 1] and fingerTime > 1:
                break
            prevFingerLoc = lmList[8]

        if action == "mouse_click":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        elif action == "mouse_down":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        elif action == "mouse_up":
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        elif action == "wheel":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -5 * wheel_distance, 0)
        elif action == "wheel_down":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, int(-600 * frameTime), 0)
        elif action == "wheel_up":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, int(600 * frameTime), 0)

        if action != "none":
            print(action)

        if isShow:
            cv2.putText(img, str(fingerState), (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    #stop_listening(wait_for_stop=False)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv)

#TODO: right hand only
#TODO: accelerate cursor adjust
#TODO: double click