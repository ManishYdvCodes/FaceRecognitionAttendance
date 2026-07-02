"""
Face Capture Module
====================
Opens a small form to collect the Student ID and Name, then starts the
webcam and captures face samples for that student.

Fix notes (see chat for full explanation):
- The old version used input() in the terminal, which blocks execution
  and is easy to miss when launched from a GUI dashboard. Replaced with
  a Tkinter form so the whole flow stays inside windows, not the console.
- Added validation so an empty Student ID can't start the camera.
- Added a clear on-screen message if the webcam fails to open.
"""

import cv2
import os
import tkinter as tk
from tkinter import messagebox

# Load Haar Cascade once, at import time, so we fail fast with a clear
# message if the file is missing instead of failing deep inside the loop.
CASCADE_PATH = "haarcascade_frontalface_default.xml"


def run_face_capture(student_id, student_name=""):
    """Opens the webcam and captures up to 50 face samples for student_id."""

    if not os.path.exists(CASCADE_PATH):
        messagebox.showerror(
            "Missing File",
            f"Could not find '{CASCADE_PATH}'.\n"
            "Make sure it is in the same folder as this script."
        )
        return

    face_detector = cv2.CascadeClassifier(CASCADE_PATH)

    os.makedirs("dataset", exist_ok=True)

    # Faster webcam startup on Windows
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cam.isOpened():
        messagebox.showerror(
            "Camera Error",
            "Could not access the webcam.\n\n"
            "Check that:\n"
            "- No other app is using the camera\n"
            "- The camera is connected/enabled\n"
            "- You've granted camera permission to Python"
        )
        return

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    count = 0
    print(f"Capturing face samples for Student ID: {student_id} ({student_name})")

    while True:
        ret, img = cam.read()

        if not ret:
            print("Camera not detected.")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            count += 1
            face = gray[y:y + h, x:x + w]

            cv2.imwrite(f"dataset/User.{student_id}.{count}.jpg", face)

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img, f"Samples: {count}/50", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )

        cv2.putText(
            img, "Press ESC to stop early", (10, img.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
        )

        cv2.imshow("Face Capture", img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if count >= 50:
            break

    cam.release()
    cv2.destroyAllWindows()

    print(f"Successfully captured {count} images.")
    messagebox.showinfo(
        "Capture Complete",
        f"Captured {count} face samples for Student ID {student_id}.\n\n"
        "You can now run 'Train Model' to update the recognizer."
    )


def launch_capture_form():
    """Small form window to collect Student ID / Name before starting the camera."""

    form = tk.Tk()
    form.title("Capture Face - Enter Student Details")
    form.geometry("380x220")
    form.configure(bg="#0f1729")

    tk.Label(
        form, text="Face Capture", font=("Segoe UI", 14, "bold"),
        bg="#0f1729", fg="white"
    ).pack(pady=(20, 10))

    tk.Label(
        form, text="Student ID", font=("Segoe UI", 10),
        bg="#0f1729", fg="#94a3b8"
    ).pack(anchor="w", padx=30)
    id_entry = tk.Entry(form, font=("Segoe UI", 11))
    id_entry.pack(fill="x", padx=30, pady=(2, 10))

    tk.Label(
        form, text="Student Name (optional, for confirmation only)",
        font=("Segoe UI", 10), bg="#0f1729", fg="#94a3b8"
    ).pack(anchor="w", padx=30)
    name_entry = tk.Entry(form, font=("Segoe UI", 11))
    name_entry.pack(fill="x", padx=30, pady=(2, 15))

    def start_capture():
        student_id = id_entry.get().strip()
        student_name = name_entry.get().strip()

        if not student_id:
            messagebox.showwarning("Missing ID", "Please enter a Student ID before starting.")
            return

        if not student_id.isdigit():
            # IDs are matched against the trained recognizer by integer label,
            # so non-numeric IDs would silently break training/recognition later.
            messagebox.showwarning(
                "Invalid ID",
                "Student ID must be numeric (it's used as the face-recognition label)."
            )
            return

        form.destroy()
        run_face_capture(student_id, student_name)

    tk.Button(
        form, text="Start Camera & Capture", font=("Segoe UI", 11, "bold"),
        bg="#3b82f6", fg="white", relief="flat", padx=10, pady=8,
        command=start_capture, cursor="hand2"
    ).pack(pady=5)

    form.mainloop()


if __name__ == "__main__":
    launch_capture_form()