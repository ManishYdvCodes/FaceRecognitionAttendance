import tkinter as tk
import sqlite3
import pandas as pd
import os

root = tk.Tk()
root.title("Attendance Analytics")
root.geometry("400x300")

# Total Students
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM students")
total_students = cursor.fetchone()[0]

conn.close()

# Present Students
filename = "attendance/attendance.csv"

if os.path.exists(filename):

    df = pd.read_csv(filename)

    present_students = len(df)

else:
    present_students = 0

absent_students = total_students - present_students

if total_students > 0:
    percentage = (present_students / total_students) * 100
else:
    percentage = 0

tk.Label(
    root,
    text=f"Total Students: {total_students}",
    font=("Arial", 14)
).pack(pady=10)

tk.Label(
    root,
    text=f"Present Students: {present_students}",
    font=("Arial", 14)
).pack(pady=10)

tk.Label(
    root,
    text=f"Absent Students: {absent_students}",
    font=("Arial", 14)
).pack(pady=10)

tk.Label(
    root,
    text=f"Attendance Percentage: {percentage:.2f}%",
    font=("Arial", 14)
).pack(pady=10)

root.mainloop()