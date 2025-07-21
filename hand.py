import cv2
import mediapipe as mp
import pyautogui
import time
import math
import os
import pygetwindow as gw
import win32gui
import win32con

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF logs

def make_window_always_on_top(window_title="Hand Tracking"):
    try:
        hwnd = gw.getWindowsWithTitle(window_title)[0]._hWnd
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    except IndexError:
        pass

# Setup
cam = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

screen_w, screen_h = pyautogui.size()
last_click = time.time()

# Cursor scaling setup
scale_factor = 2.7
prev_wrist_x, prev_wrist_y = None, None
cursor_x, cursor_y = pyautogui.position()

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hands.process(rgb_color)
    land_marks = output.multi_hand_landmarks

    if land_marks:
        h, w, _ = frame.shape
        for hand_landmarks in land_marks:
            landmarks = hand_landmarks.landmark
            wrist = landmarks[9]

            # Get normalized wrist position
            norm_x, norm_y = wrist.x, wrist.y

            # Convert to screen coordinates (baseline)
            curr_wrist_x = int(norm_x * screen_w)
            curr_wrist_y = int(norm_y * screen_h)

            # On first frame, just set initial values
            if prev_wrist_x is None:
                prev_wrist_x, prev_wrist_y = curr_wrist_x, curr_wrist_y

            # Calculate movement deltas
            dx = (curr_wrist_x - prev_wrist_x) * scale_factor
            dy = (curr_wrist_y - prev_wrist_y) * scale_factor

            # Update cursor position
            cursor_x += dx
            cursor_y += dy

            # Clamp cursor within screen bounds
            cursor_x = max(0, min(screen_w - 1, cursor_x))
            cursor_y = max(0, min(screen_h - 1, cursor_y))

            pyautogui.moveTo(cursor_x, cursor_y)
            prev_wrist_x, prev_wrist_y = curr_wrist_x, curr_wrist_y

            # Draw wrist point
            cx, cy = int(wrist.x * w), int(wrist.y * h)
            cv2.circle(frame, (cx, cy), 6, (0, 255, 0), -1)

            # Thumb & Index
            thumb = landmarks[4]
            index = landmarks[8]
            thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)
            index_x, index_y = int(index.x * w), int(index.y * h)

            cv2.circle(frame, (thumb_x, thumb_y), 6, (255, 0, 0), -1)
            cv2.circle(frame, (index_x, index_y), 6, (0, 0, 255), -1)

            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            # Click gesture
            if distance < 15 and (time.time() - last_click) > 2:
                pyautogui.click()
                last_click = time.time()
                print("🖱️ Clicked!")

            # Scroll gesture
            elif distance > 102 and (time.time() - last_click) > 1:
                pyautogui.scroll(-500)
                last_click = time.time()

    # Show the window and keep it always on top
    cv2.imshow('Hand Tracking', frame)
    make_window_always_on_top("Hand Tracking")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
