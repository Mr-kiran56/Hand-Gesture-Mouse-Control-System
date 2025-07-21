import cv2
import pyautogui
import mediapipe as mp
import time

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
last_click = 0

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    output = face_mesh.process(rgb_frame)
    land_marks = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape  

    if land_marks:
        landmarks = land_marks[0].landmark
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 1, (200, 0, 29), -1)
            if id == 1:
                screen_x = screen_w / frame_w * x
                screen_y = screen_h / frame_h * y
                pyautogui.moveTo(screen_x, screen_y)

        left = [landmarks[145], landmarks[159]]
        for mark in left:
            x = int(mark.x * frame_w)
            y = int(mark.y * frame_h)
            cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

        if (left[0].y - left[1].y) < 0.009:
            if time.time() - last_click > 1:
                pyautogui.click()
                last_click = time.time()
                print('clicked')

    cv2.imshow('Eye Controlled Mouse', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
