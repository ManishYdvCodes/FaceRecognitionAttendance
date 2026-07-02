# view_students_gui.py

import tkinter as tk
import sqlite3

root = tk.Tk()

root.title("Students")

conn = sqlite3.connect("students.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM students")

rows = cursor.fetchall()

for row in rows:
    tk.Label(
        root,
        text=str(row)
    ).pack()

root.mainloop()

conn.close()