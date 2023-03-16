import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
count = 0
current_hand_status = "normal"
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # 웹캠을 찾지 못했을 때
            continue

        # 좌우 반전
        # BGR 에서 RGB로
        
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        black_canvas = np.zeros(image.shape, dtype="uint8")
        sh, sw, _ = image.shape
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = hands.process(image)

        # 손 트래킹
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x, y = hand_landmarks.landmark[9].x*sw, hand_landmarks.landmark[9].y*sh
                x1, y1 = hand_landmarks.landmark[12].x*sw, hand_landmarks.landmark[12].y*sh

                cv2.circle(black_canvas, (int(x), int(y)), 10, (0, 255, 0), -1)
                # cv2.circle(image, (int(x1), int(y1)), 10, (0, 0, 255), -1)
                

                if y1 > y:
                    # 손을 쥐었을 때
                    # 1. 위치를 나타내는 원의 색 변경
                    # 2. 그 공간에 박스 표시
                    hand_status = "grab"
                    cv2.circle(black_canvas, (int(x), int(y)), 10, (0, 255, 255), -1)
                    
                    # 손의 위치에 따라 블럭 표시
                    if 0.25*sw >x1:
                        cv2.rectangle(black_canvas, pt1=(0, 0), pt2=(int(0.25*sw), sh), color=(255,0,0), thickness=-1)
                    elif 0.25 < x1 and 0.50*sw >x1:
                        cv2.rectangle(black_canvas, pt1=(int(0.25*sw), 0), pt2=(int(0.50*sw), sh), color=(255,0,0), thickness=-1)
                    elif 0.50 < x1 and 0.75*sw >x1:
                        cv2.rectangle(black_canvas, pt1=(int(0.50*sw), 0), pt2=(int(0.75*sw), sh), color=(255,0,0), thickness=-1)
                    elif 0.75 < x1:
                        cv2.rectangle(black_canvas, pt1=(int(0.75*sw), 0), pt2=(sw, sh), color=(255,0,0), thickness=-1)
                else:
                    hand_status = "normal"
                if current_hand_status != hand_status and hand_status == 'grab':
                    count += 1
                current_hand_status = hand_status
                
                
                # 상태가 바뀌면 count 올라가기
                cv2.putText(black_canvas, f'count: {count}', (50, 50), 0, 1, (0, 0, 255), 2)
                cv2.putText(black_canvas, hand_status, (50, 100), 0, 1, (0, 0, 255), 2)

        cv2.imshow('MediaPipe Hands', black_canvas)
        cv2.imshow('camera', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)