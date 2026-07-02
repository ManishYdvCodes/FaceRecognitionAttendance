import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

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

plt.figure(figsize=(6,6))

plt.pie(
    [present_students, absent_students],
    labels=["Present", "Absent"],
    autopct="%1.1f%%"
)

plt.title("Attendance Analysis")

plt.show()