import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database Connection
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create Table if Not Exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    year TEXT
)
""")

conn.commit()


def register_student():

    student_id = entry_id.get()
    name = entry_name.get()
    department = entry_department.get()
    year = entry_year.get()

    try:

        cursor.execute(
            """
            INSERT INTO students
            (id,name,department,year)
            VALUES
            (?,?,?,?)
            """,
            (
                student_id,
                name,
                department,
                year
            )
        )

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Student Registered Successfully"
        )

        entry_id.delete(0, tk.END)
        entry_name.delete(0, tk.END)
        entry_department.delete(0, tk.END)
        entry_year.delete(0, tk.END)

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


# Main Window
root = tk.Tk()

root.title(
    "Student Registration"
)

root.geometry("400x300")

# Labels
tk.Label(
    root,
    text="Student ID"
).pack()

entry_id = tk.Entry(root)
entry_id.pack()

tk.Label(
    root,
    text="Name"
).pack()

entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(
    root,
    text="Department"
).pack()

entry_department = tk.Entry(root)
entry_department.pack()

tk.Label(
    root,
    text="Year"
).pack()

entry_year = tk.Entry(root)
entry_year.pack()

# Button
tk.Button(
    root,
    text="Register Student",
    command=register_student
).pack(pady=15)

root.mainloop()

conn.close()