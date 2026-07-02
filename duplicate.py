import tkinter as tk
import subprocess
from PIL import Image, ImageTk
from datetime import datetime

root = tk.Tk()
root.configure(bg="#666279")
image = Image.open(
    "images/logo.png"
)

image = image.resize(
    (150,150)
)

logo = ImageTk.PhotoImage(image)

logo_label = tk.Label(
    root,
    image=logo,
    bg="#121212"
)

logo_label.pack(pady=10)

root.title("Face Recognition Attendance System")

root.geometry("1200x800")

title = tk.Label(
    root,
    text="FACE RECOGNITION ATTENDANCE SYSTEM",
    font=("Arial", 22, "bold"),
    bg="#121212",
    fg="white"
)
title.pack(pady=20)

time_label = tk.Label(
    root,
    font=("Arial", 12, "bold"),
    bg="#121212",
    fg="white"
)

time_label.pack(pady=5)

def update_time():

    current_time = datetime.now().strftime(
        "Date: %d-%m-%Y    Time: %H:%M:%S"
    )

    time_label.config(text=current_time)

    root.after(1000, update_time)

def register_student():
    subprocess.Popen(["python", "student_registration.py"])

def capture_face():
    subprocess.Popen(["python", "register.py"])

def train_model():
    subprocess.Popen(["python", "train.py"])

def mark_attendance():
    subprocess.Popen(["python", "attendance.py"])

def view_students():
    subprocess.Popen(["python", "view_students_gui.py"])

def view_attendance():
    subprocess.Popen(["python", "view_attendance_gui.py"])

def attendance_analytics():
    subprocess.Popen(["python", "attendance_analytics.py"])

def attendance_chart():
    subprocess.Popen(["python", "attendance_chart.py"])

# Buttons
tk.Button(
    root,
    text="Register Student",
    width=30,
    height=2,
    command=register_student
).pack(pady=5)

tk.Button(
    root,
    text="Capture Face",
    width=30,
    height=2,
    command=capture_face
).pack(pady=5)

tk.Button(
    root,
    text="Train Model",
    width=30,
    height=2,
    command=train_model
).pack(pady=5)

tk.Button(
    root,
    text="Mark Attendance",
    width=30,
    height=2,
    command=mark_attendance
).pack(pady=5)
tk.Button(
    root,
    text="View Students",
    width=30,
    height=2,
    command=view_students
).pack(pady=5)
tk.Button(
    root,
    text="View Attendance",
    width=30,
    height=2,
    command=view_attendance
).pack(pady=5)

tk.Button(
    root,
    text="Attendance Analytics",
    width=30,
    height=2,
    command=attendance_analytics
).pack(pady=5)

tk.Button(
    root,
    text="Attendance Chart",
    width=30,
    height=2,
    command=attendance_chart
).pack(pady=5)
tk.Button(
    root,
    text="Exit",
    width=30,
    height=2,
    command=root.destroy
).pack(pady=5)

update_time()
footer = tk.Label(
    root,
    text="Developed by Manish Yadav | Enrollment No: 2023-310-100",
    font=("Arial", 9),
    bg="#121212",
    fg="lightgray"
)

footer.pack(side="bottom", pady=8)
root.mainloop()