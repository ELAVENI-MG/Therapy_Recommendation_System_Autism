import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")

scanpath = []


def process_frame(frame):
    global scanpath

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    gaze_x, gaze_y = None, None

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes[:2]:  # only 2 eyes
            cx = x + ex + ew // 2
            cy = y + ey + eh // 2

            scanpath.append((cx, cy))

            gaze_x = int(cx)
            gaze_y = int(cy)

    return gaze_x, gaze_y


def get_features():
    global scanpath

    if len(scanpath) < 2:
        return 0, 0

    distances = []

    for i in range(len(scanpath) - 1):
        d = np.linalg.norm(
            np.array(scanpath[i]) - np.array(scanpath[i+1])
        )
        distances.append(d)

    fixation_count = len(scanpath)
    avg_movement = float(np.mean(distances))

    return fixation_count, avg_movement


def reset_scanpath():
    global scanpath
    scanpath = []