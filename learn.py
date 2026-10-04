import cv2
import mediapipe as mp
import numpy as np
from maths import acos, degree

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture("bdysqtv1.mp4")

with mp_pose.Pose(
    static_image_mode=False) as pose:
    
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        #frame =cv.2flip(frame, 1)
        height,width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks is not None:
            
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()     