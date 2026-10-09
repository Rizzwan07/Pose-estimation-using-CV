# Computer Vision Squat Counter

A webcam-based squat counter built with Flask, OpenCV, MediaPipe Pose, and NumPy. The application uses computer vision pose estimation to locate body landmarks in real time, measures the angle at the left knee, counts valid squats, and displays feedback over a live browser video stream. Squat classification is based on geometric angle calculations and fixed thresholds.

## Features

- Live webcam video in a browser dashboard
- MediaPipe pose landmarks and skeleton overlay
- Real-time left knee angle display
- Automatic squat repetition counting
- Feedback for standing position, depth, and invalid repetitions
- Counter reset when the page is refreshed

## Requirements

- Python 3.9 or newer
- A working webcam
- Permission for Python to access the webcam
- A modern web browser

The application depends on:

- Flask
- OpenCV (`opencv-python`)
- MediaPipe
- NumPy

## Installation

1. Clone or download this project and open a terminal in the project directory.
2. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install Flask opencv-python mediapipe numpy
   ```

## Running the application

Start the Flask server:

```powershell
python main.py
```

Open the URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

Allow camera access if the browser or operating system asks for permission. Stand where your left side is visible to the camera and perform squats in view of the webcam. Refresh the page to reset the repetition counter.

## Squat-counting logic

The application calculates the angle formed by the left hip, left knee, and left ankle:

- Above `160` degrees: standing position; a valid repetition is completed if the user previously reached the valid down position.
- Between `65` and `90` degrees: valid squat depth.
- Below `65` degrees: the repetition is marked as too deep and is not counted.
- Between `90` and `130` degrees while standing: the user is prompted to go deeper.

A repetition is counted only after the user reaches the valid depth range and then returns to a standing position. The counter is stored in application memory and resets when the home page is loaded or the server restarts.

## Application routes

| Route         | Purpose                                                |
| ------------- | ------------------------------------------------------ |
| `/`           | Loads the web dashboard and resets the counter state   |
| `/video_feed` | Streams the annotated webcam feed as an MJPEG response |
| `/stats`      | Returns the current repetition count as JSON           |

## Project structure

```text
.
├── main.py              # Flask application and squat detection logic
├── templates/
│   └── index.html       # Browser dashboard
├── bodylandmark.py      # Standalone MediaPipe full-body landmark demo
├── cv.py                # Basic webcam capture experiment
├── recordnsave.py       # Webcam recording experiment
├── test2.py             # Video-file squat angle and count experiment
├── learn.py             # Earlier pose-detection experiment
└── README.md
```

The standalone scripts are exploratory examples and are not needed to run the Flask application. `main.py` is the project entry point.

## Troubleshooting

- **Camera does not open:** close other applications using the webcam and check Windows camera permissions.
- **No pose or inaccurate counts:** make sure the whole body side profile is visible, lighting is sufficient, and the left hip, knee, and ankle are not obstructed.
- **Import errors:** activate the virtual environment and run the dependency installation command again.
- **Port already in use:** stop the other process using port `5000`, or change the `app.run` port in `main.py`.

## Notes

The server runs with Flask debug mode enabled for local development. Do not expose this development server directly to the public internet without adding appropriate production serving and security configuration.
