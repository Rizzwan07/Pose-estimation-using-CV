from flask import Flask, render_template, Response, jsonify
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
stage = "up"  # tracks state: 'up', 'down', or 'too_deep'
feedback = "Stand in frame"
invalid_rep = False  # Locks if user drops < 65 deg to prevent counting on ascent

def generate_frames():
    global counter, stage, feedback, invalid_rep
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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
                # 1. Extreme depth / collapse: disqualify rep immediately
                if knee_angle < 65:
                    invalid_rep = True
                    stage = "too_deep"
                    feedback = "Too Deep!"

                # 2. Valid depth zone (65° to 90°): only valid if not flagged as too deep
                elif 65 <= knee_angle <= 90:
                    if not invalid_rep:
                        stage = "down"
                        feedback = "Good Depth"
                    else:
                        feedback = "Too Deep!"

                # 3. Midway zone
                elif 90 < knee_angle < 130 and stage == "up":
                    feedback = "Go Deeper"

                # 4. Standing tall (completed rep)
                elif knee_angle > 160:
                    if stage == "down" and not invalid_rep:
                        counter += 1
                        feedback = "Good Rep!"
                    elif invalid_rep:
                        feedback = "No Rep: Went Too Deep"
                    else:
                        feedback = "Squat Down"

                    # Reset states for the next rep
                    stage = "up"
                    invalid_rep = False

            except Exception:
                pass
            
            # Overlay dashboard inside video frame
            cv2.rectangle(image, (0, 0), (320, 85), (20, 20, 20), -1)
            cv2.putText(image, f"REPS: {counter}", (15, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"{feedback}", (15, 68), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 215, 255) if "Too" in feedback or "Go" in feedback else (200, 200, 200), 2, cv2.LINE_AA)
            
            # Draw skeleton
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
            ret_encode, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()

@app.route('/')
def index():
    global counter, stage, feedback, invalid_rep
    counter = 0  # Reset on page refresh
    stage = "up"
    feedback = "Stand in frame"
    invalid_rep = False
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    global counter
    return jsonify({'counter': counter})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)