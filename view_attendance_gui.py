"""
View Attendance Module
========================
Displays attendance records in a table, with:
- a visible "Total records" counter (this was missing before)
- a dropdown to pick which day's attendance file to view (the old version
  only ever looked at today's file, so any other day's session looked
  "empty" with no explanation)
- a Refresh button
- a friendly message instead of a silently blank table when no file exists
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import glob
import re
from datetime import datetime

ATTENDANCE_DIR = "attendance"


def list_attendance_dates():
    """Returns sorted list of dates (YYYY_MM_DD) for which a CSV exists, newest first."""
    if not os.path.isdir(ATTENDANCE_DIR):
        return []

    pattern = os.path.join(ATTENDANCE_DIR, "Attendance_*.csv")
    dates = []
    for path in glob.glob(pattern):
        match = re.search(r"Attendance_(\d{4}_\d{2}_\d{2})\.csv$", os.path.basename(path))
        if match:
            dates.append(match.group(1))

    dates.sort(reverse=True)
    return dates


class AttendanceViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Records")
        self.root.geometry("760x480")
        self.root.configure(bg="#0f1729")

        self._build_top_bar()
        self._build_table()
        self._build_count_bar()

        self.refresh()

    def _build_top_bar(self):
        bar = tk.Frame(self.root, bg="#0f1729")
        bar.pack(fill="x", padx=15, pady=12)

        tk.Label(
            bar, text="Date:", font=("Segoe UI", 10, "bold"),
            bg="#0f1729", fg="white"
        ).pack(side="left", padx=(0, 6))

        self.date_var = tk.StringVar()
        self.date_dropdown = ttk.Combobox(
            bar, textvariable=self.date_var, state="readonly", width=15
        )
        self.date_dropdown.pack(side="left")
        self.date_dropdown.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        tk.Button(
            bar, text="Refresh", command=self.refresh,
            bg="#3b82f6", fg="white", relief="flat", padx=12, pady=4, cursor="hand2"
        ).pack(side="left", padx=10)

    def _build_table(self):
        table_frame = tk.Frame(self.root, bg="#0f1729")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 5))

        self.tree = ttk.Treeview(
            table_frame, columns=("ID", "Name", "Time"), show="headings"
        )
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Time", text="Time Marked")
        self.tree.column("ID", width=120, anchor="center")
        self.tree.column("Name", width=300)
        self.tree.column("Time", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_count_bar(self):
        bar = tk.Frame(self.root, bg="#141d31")
        bar.pack(fill="x", side="bottom")

        self.count_label = tk.Label(
            bar, text="Total records: 0", font=("Segoe UI", 10, "bold"),
            bg="#141d31", fg="#22c55e", anchor="w", padx=15, pady=8
        )
        self.count_label.pack(side="left")

        self.empty_message = tk.Label(
            self.root, text="", font=("Segoe UI", 11), bg="#0f1729", fg="#94a3b8"
        )

    def refresh(self):
        dates = list_attendance_dates()

        # Repopulate the dropdown, preserving the current selection if possible.
        current_selection = self.date_var.get()
        readable_dates = [d for d in dates]
        self.date_dropdown["values"] = readable_dates

        if not readable_dates:
            self.date_var.set("")
            self._show_empty("No attendance files found yet.\nRun 'Mark Attendance' first.")
            self.count_label.config(text="Total records: 0")
            return

        if current_selection not in readable_dates:
            self.date_var.set(readable_dates[0])  # default to most recent date

        selected_date = self.date_var.get()
        filename = os.path.join(ATTENDANCE_DIR, f"Attendance_{selected_date}.csv")

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not os.path.exists(filename):
            self._show_empty(f"No file found for {selected_date}.")
            self.count_label.config(text="Total records: 0")
            return

        try:
            df = pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["ID", "Name", "Time"])

        if df.empty:
            self._show_empty(f"No attendance recorded on {selected_date}.")
            self.count_label.config(text="Total records: 0")
            return

        self._hide_empty()

        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=(row["ID"], row["Name"], row["Time"]))

        self.count_label.config(text=f"Total records: {len(df)}  ·  Date: {selected_date}")

    def _show_empty(self, message):
        self.tree.pack_forget()
        self.empty_message.config(text=message)
        self.empty_message.pack(expand=True)

    def _hide_empty(self):
        self.empty_message.pack_forget()
        if not self.tree.winfo_ismapped():
            self.tree.pack(side="left", fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceViewer(root)
    root.mainloop()