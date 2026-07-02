"""
Mark Attendance Module
========================
Runs live face recognition against the trained model and logs attendance
to a daily CSV file.

Fix notes (see chat for full explanation):
- Original code crashed with FileNotFoundError if the 'attendance/' folder
  didn't exist yet, because df.to_csv() doesn't create folders. Added
  os.makedirs(..., exist_ok=True) before saving.
- Added a check for missing trainer.yml / cascade file so it fails with a
  clear message instead of a cryptic OpenCV traceback.
- Added a check for camera failing to open.
- Even if zero faces are recognized in a session, we still create the CSV
  (with headers only) so view_attendance_gui.py has something consistent
  to read, and we tell the user how many people were marked when the
  window closes.
"""

import os
import sqlite3
import cv2
import pandas as pd
from datetime import datetime

TRAINER_PATH = "trainer/trainer.yml"
CASCADE_PATH = "haarcascade_frontalface_default.xml"
DB_PATH = "students.db"
ATTENDANCE_DIR = "attendance"


def main():
    if not os.path.exists(TRAINER_PATH):
        print(f"ERROR: '{TRAINER_PATH}' not found. Run 'Train Model' first.")
        return

    if not os.path.exists(CASCADE_PATH):
        print(f"ERROR: '{CASCADE_PATH}' not found in this folder.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)

    faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("ERROR: Could not access the webcam.")
        conn.close()
        return

    attendance = []
    marked_ids = set()

    print("Attendance session started. Press ENTER (in the camera window) to stop.")

    while True:
        ret, img = cam.read()
        if not ret:
            print("Camera read failed.")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            id_, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 60:
                cursor.execute("SELECT name FROM students WHERE id=?", (id_,))
                result = cursor.fetchone()
                name = result[0] if result else "Unknown"

                if id_ not in marked_ids:
                    time_now = datetime.now()
                    attendance.append([id_, name, time_now.strftime("%H:%M:%S")])
                    marked_ids.add(id_)
                    print(f"Attendance marked for {name} (ID: {id_})")

                cv2.putText(img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                cv2.putText(img, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.putText(
            img, f"Marked: {len(marked_ids)}  |  Press ENTER to finish", (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
        )

        cv2.imshow("Attendance System", img)

        if cv2.waitKey(1) == 13:  # Press Enter
            break

    cam.release()
    cv2.destroyAllWindows()
    conn.close()

    # --- Save attendance (always, even if empty, so the CSV exists) ---
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)

    df = pd.DataFrame(attendance, columns=["ID", "Name", "Time"])
    today = datetime.now().strftime("%Y_%m_%d")
    filename = os.path.join(ATTENDANCE_DIR, f"Attendance_{today}.csv")

    # If a file for today already exists (e.g. ran attendance twice today),
    # append new entries instead of overwriting the earlier session.
    if os.path.exists(filename):
        existing = pd.read_csv(filename)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.drop_duplicates(subset=["ID"], keep="first", inplace=True)
        combined.to_csv(filename, index=False)
    else:
        df.to_csv(filename, index=False)

    print(f"Session complete. {len(attendance)} student(s) marked. Saved to {filename}")


if __name__ == "__main__":
    main()