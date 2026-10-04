from flask import Flask, render_template, Response , jsonify
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0]) #it give angle between shin and thigh
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360.0 - angle
        
    return angle

counter = 0
stage = "up"  # tracks state: 'up' or 'down'
feedback = "Stand in frame"

def generate_frames():
    global counter, stage, feedback
    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            
            # Recolor back to BGR for rendering
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Using left side landmarks 
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                
                # Compute knee flexion angle
                knee_angle = calculate_angle(hip, knee, ankle)
                
                # Convert knee coordinates to pixel space for displaying angle text
                h, w, _ = image.shape
                knee_px = tuple(np.multiply(knee, [w, h]).astype(int))
                cv2.putText(image, f"{int(knee_angle)} deg", knee_px, 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Rep counting & depth logic
                # Standing: 160° - 180° | Deep Squat: <= 90°
                if knee_angle > 160:
                    if stage == "down":
                        counter += 1
                    stage = "up"
                    feedback = "Good"
                elif knee_angle <= 90:
                    stage = "down"
                    feedback = "Deep Squat"
                elif knee_angle < 120 and stage == "up":
                    feedback = "Go Lower"

            except Exception:
                pass
            
            # Overlay dashboard
            cv2.rectangle(image, (0, 0), (280, 85), (20, 20, 20), -1)
            cv2.putText(image, f"REPS: {counter}", (15, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"STAGE: {stage.upper()} | {feedback}", (15, 65), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
            
            # Draw skeleton
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
            ret_encode, buffer = cv2.imencode('.jpg', image)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)