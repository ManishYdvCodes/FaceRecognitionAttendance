# view_students_gui.py
#
# Shows all registered students, with a "Clear All & Start Fresh" button
# that wipes the students table, deletes face images, and the trained
# model - so you can go back to registering students one by one from
# a clean slate, using the normal Register Student -> Capture Face ->
# Train Model flow for each new student.

import os
import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = "students.db"
DATASET_DIR = "dataset"
TRAINER_PATH = "trainer/trainer.yml"

root = tk.Tk()
root.title("Students")
root.geometry("420x480")
root.configure(bg="#0f1729")

tk.Label(
    root, text="Registered Students", font=("Segoe UI", 14, "bold"),
    bg="#0f1729", fg="white"
).pack(pady=(15, 5))

list_frame = tk.Frame(root, bg="#0f1729")
list_frame.pack(fill="both", expand=True, padx=20, pady=10)

status_var = tk.StringVar()
status_label = tk.Label(
    root, textvariable=status_var, font=("Segoe UI", 9),
    bg="#0f1729", fg="#94a3b8"
)
status_label.pack(pady=(0, 5))


def load_students():
    # Clear whatever is currently shown before redrawing
    for widget in list_frame.winfo_children():
        widget.destroy()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        tk.Label(
            list_frame, text="No students registered.",
            bg="#0f1729", fg="#64748b", font=("Segoe UI", 10)
        ).pack(pady=20)
    else:
        for row in rows:
            tk.Label(
                list_frame, text=str(row), bg="#1b2638", fg="#f1f5f9",
                font=("Segoe UI", 10), anchor="w", padx=10, pady=6
            ).pack(fill="x", pady=2)

    status_var.set(f"{len(rows)} student(s) registered.")


def clear_all_students():
    confirm = messagebox.askyesno(
        "Clear All Students",
        "This will remove ALL student records, ALL captured face images, "
        "and the trained model.\n\n"
        "You can then register new students one by one from scratch.\n\n"
        "Continue?"
    )
    if not confirm:
        return

    # 1. Clear the students table
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students")
        conn.commit()
        conn.close()

    # 2. Delete all captured face images
    if os.path.exists(DATASET_DIR):
        for filename in os.listdir(DATASET_DIR):
            file_path = os.path.join(DATASET_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # 3. Delete the trained model (it still "remembers" the old faces
    #    otherwise, even after the images and records are gone)
    if os.path.exists(TRAINER_PATH):
        os.remove(TRAINER_PATH)

    load_students()
    messagebox.showinfo(
        "Cleared",
        "All students, face images, and the trained model have been cleared.\n\n"
        "Go to 'Register Student' to start adding students again, one by one."
    )


button_row = tk.Frame(root, bg="#0f1729")
button_row.pack(fill="x", padx=20, pady=(0, 15))

tk.Button(
    button_row, text="Refresh", font=("Segoe UI", 10, "bold"),
    bg="#3b82f6", fg="white", relief="flat", padx=12, pady=6,
    command=load_students, cursor="hand2"
).pack(side="left")

tk.Button(
    button_row, text="Clear All & Start Fresh", font=("Segoe UI", 10, "bold"),
    bg="#ef4444", fg="white", relief="flat", padx=12, pady=6,
    command=clear_all_students, cursor="hand2"
).pack(side="right")

load_students()
root.mainloop()