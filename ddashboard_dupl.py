"""
Face Recognition Attendance System — Main Dashboard
=====================================================
This is the main control panel of the project. Every other script
(registration, training, attendance marking, reports, etc.) is launched
from here as a separate process, so this file only deals with the GUI.

Author : Manish Yadav
Enroll : 2023-310-100
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from datetime import datetime
from PIL import Image, ImageTk


# ----------------------------------------------------------------------
# 1. THEME / CONSTANTS
# ----------------------------------------------------------------------
# Keeping all colors and fonts in one place means we can re-theme the
# whole app by editing values here instead of hunting through the file.

class Theme:
    BG_DARK = "#0f1729"        # main window background
    BG_SIDEBAR = "#141d31"     # left sidebar background
    BG_CARD = "#1b2638"        # button "card" background
    BG_CARD_HOVER = "#243049"  # button "card" on mouse-hover
    ACCENT = "#3b82f6"         # primary accent (blue)
    ACCENT_HOVER = "#2563eb"
    SUCCESS = "#22c55e"        # green accent for "Mark Attendance"
    DANGER = "#ef4444"         # red accent for "Exit"
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"

    FONT_FAMILY = "Segoe UI"   # falls back gracefully on non-Windows systems
    FONT_TITLE = (FONT_FAMILY, 22, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 11)
    FONT_SECTION = (FONT_FAMILY, 10, "bold")
    FONT_BUTTON = (FONT_FAMILY, 12, "bold")
    FONT_BUTTON_DESC = (FONT_FAMILY, 8)
    FONT_CLOCK = (FONT_FAMILY, 11, "bold")
    FONT_FOOTER = (FONT_FAMILY, 9)


# ----------------------------------------------------------------------
# 2. REUSABLE HOVER-BUTTON CARD
# ----------------------------------------------------------------------
# Instead of plain tk.Button (which looks dated), each action is a small
# "card": an icon + title + one-line description, with a colored left
# accent bar and a hover effect. This is the same visual pattern used in
# real admin dashboards (icon-led action cards).

class ActionCard(tk.Frame):
    def __init__(self, parent, icon, title, description, command,
                 accent=Theme.ACCENT, **kwargs):
        super().__init__(parent, bg=Theme.BG_CARD, cursor="hand2", **kwargs)
        self.command = command
        self.accent = accent

        # thin colored bar on the left edge of the card
        self.accent_bar = tk.Frame(self, bg=accent, width=4)
        self.accent_bar.pack(side="left", fill="y")

        content = tk.Frame(self, bg=Theme.BG_CARD)
        content.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        top_row = tk.Frame(content, bg=Theme.BG_CARD)
        top_row.pack(fill="x", anchor="w")

        icon_label = tk.Label(
            top_row, text=icon, font=("Segoe UI Emoji", 16),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        )
        icon_label.pack(side="left", padx=(0, 8))

        title_label = tk.Label(
            top_row, text=title, font=Theme.FONT_BUTTON,
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, anchor="w"
        )
        title_label.pack(side="left")

        desc_label = tk.Label(
            content, text=description, font=Theme.FONT_BUTTON_DESC,
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY, anchor="w", justify="left"
        )
        desc_label.pack(fill="x", anchor="w", pady=(2, 0))

        # All child widgets need the same hover + click behaviour, so we
        # bind every one of them, not just the outer frame.
        clickable_widgets = [self, content, top_row, icon_label, title_label, desc_label]
        for widget in clickable_widgets:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

        self._bg_widgets = [self, content, top_row, icon_label, title_label, desc_label]

    def _on_click(self, _event):
        if self.command:
            self.command()

    def _on_enter(self, _event):
        for widget in self._bg_widgets:
            widget.configure(bg=Theme.BG_CARD_HOVER)

    def _on_leave(self, _event):
        for widget in self._bg_widgets:
            widget.configure(bg=Theme.BG_CARD)


# ----------------------------------------------------------------------
# 3. MAIN APPLICATION
# ----------------------------------------------------------------------

class AttendanceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=Theme.BG_DARK)

        self.status_var = tk.StringVar(value="System ready.")

        self._build_sidebar()
        self._build_main_area()
        self._update_clock()

    # ------------------------------------------------------------------
    # SIDEBAR (logo + branding)
    # ------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = tk.Frame(self.root, bg=Theme.BG_SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)  # keep fixed width regardless of contents

        logo_holder = tk.Frame(sidebar, bg=Theme.BG_SIDEBAR)
        logo_holder.pack(pady=(30, 10))

        logo_path = os.path.join("images", "logo.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path).resize((90, 90))
            self.logo_img = ImageTk.PhotoImage(image)  # keep reference alive
            tk.Label(logo_holder, image=self.logo_img, bg=Theme.BG_SIDEBAR).pack()
        else:
            # graceful fallback so missing logo file never crashes the app
            tk.Label(
                logo_holder, text="📷", font=("Segoe UI Emoji", 40),
                bg=Theme.BG_SIDEBAR, fg=Theme.ACCENT
            ).pack()

        tk.Label(
            sidebar, text="ATTENDANCE", font=(Theme.FONT_FAMILY, 14, "bold"),
            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_PRIMARY
        ).pack(pady=(5, 0))
        tk.Label(
            sidebar, text="FACE RECOGNITION SYSTEM", font=(Theme.FONT_FAMILY, 8),
            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY
        ).pack()

        tk.Frame(sidebar, bg=Theme.ACCENT, height=2).pack(fill="x", padx=30, pady=20)

        # quick status / info panel
        info_frame = tk.Frame(sidebar, bg=Theme.BG_SIDEBAR)
        info_frame.pack(fill="x", padx=20, pady=10)

        for label, value in [
            ("STATUS", "● Online"),
            ("VERSION", "v2.0"),
            ("MODE", "Administrator"),
        ]:
            row = tk.Frame(info_frame, bg=Theme.BG_SIDEBAR)
            row.pack(fill="x", pady=4)
            tk.Label(
                row, text=label, font=(Theme.FONT_FAMILY, 8, "bold"),
                bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED
            ).pack(anchor="w")
            tk.Label(
                row, text=value, font=(Theme.FONT_FAMILY, 10),
                bg=Theme.BG_SIDEBAR,
                fg=Theme.SUCCESS if "Online" in value else Theme.TEXT_PRIMARY
            ).pack(anchor="w")

        # footer pinned to the bottom of the sidebar
        footer = tk.Label(
            sidebar,
            text="Developed by\nManish Yadav\nEnroll: 2023-310-100",
            font=Theme.FONT_FOOTER, bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_MUTED,
            justify="left"
        )
        footer.pack(side="bottom", pady=20, padx=20, anchor="w")

    # ------------------------------------------------------------------
    # MAIN AREA (header + action cards grid + status bar)
    # ------------------------------------------------------------------
    def _build_main_area(self):
        main = tk.Frame(self.root, bg=Theme.BG_DARK)
        main.pack(side="left", fill="both", expand=True)

        self._build_header(main)
        self._build_cards_grid(main)
        self._build_status_bar(main)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=Theme.BG_DARK)
        header.pack(fill="x", padx=30, pady=(25, 10))

        tk.Label(
            header, text="FACE RECOGNITION ATTENDANCE SYSTEM",
            font=Theme.FONT_TITLE, bg=Theme.BG_DARK, fg=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(side="left")

        clock_box = tk.Frame(header, bg=Theme.BG_CARD)
        clock_box.pack(side="right")
        self.time_label = tk.Label(
            clock_box, font=Theme.FONT_CLOCK, bg=Theme.BG_CARD,
            fg=Theme.TEXT_PRIMARY, padx=14, pady=8
        )
        self.time_label.pack()

        tk.Label(
            parent, text="Manage student enrollment, face data, and attendance records",
            font=Theme.FONT_SUBTITLE, bg=Theme.BG_DARK, fg=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x", padx=30, pady=(0, 15))

    def _build_cards_grid(self, parent):
        # We group related actions under section labels — this mirrors how
        # real dashboards organize tools (Setup vs Operations vs Reports)
        # instead of dumping eight identical buttons in one column.

        container = tk.Frame(parent, bg=Theme.BG_DARK)
        container.pack(fill="both", expand=True, padx=30, pady=5)

        sections = [
            ("SETUP", [
                ("🧑‍🎓", "Register Student", "Add new student details to the database", self.register_student, Theme.ACCENT),
                ("📸", "Capture Face", "Capture face samples for recognition", self.capture_face, Theme.ACCENT),
                ("🧠", "Train Model", "Train the recognition model on captured faces", self.train_model, Theme.ACCENT),
            ]),
            ("OPERATIONS", [
                ("✅", "Mark Attendance", "Start live face recognition attendance", self.mark_attendance, Theme.SUCCESS),
            ]),
            ("RECORDS & REPORTS", [
                ("📋", "View Students", "Browse all registered student records", self.view_students, Theme.ACCENT),
                ("🗂️", "View Attendance", "Browse logged attendance records", self.view_attendance, Theme.ACCENT),
                ("📊", "Attendance Analytics", "View attendance statistics and summaries", self.attendance_analytics, Theme.ACCENT),
                ("📈", "Attendance Chart", "Visualize attendance trends over time", self.attendance_chart, Theme.ACCENT),
            ]),
        ]

        for section_title, items in sections:
            tk.Label(
                container, text=section_title, font=Theme.FONT_SECTION,
                bg=Theme.BG_DARK, fg=Theme.TEXT_MUTED, anchor="w"
            ).pack(fill="x", pady=(12, 6))

            grid = tk.Frame(container, bg=Theme.BG_DARK)
            grid.pack(fill="x")
            # two cards per row keeps cards readable at typical window widths
            for col in range(2):
                grid.grid_columnconfigure(col, weight=1, uniform="card")

            for index, (icon, title, desc, cmd, accent) in enumerate(items):
                row, col = divmod(index, 2)
                card = ActionCard(grid, icon, title, desc, cmd, accent=accent)
                card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        exit_row = tk.Frame(container, bg=Theme.BG_DARK)
        exit_row.pack(fill="x", pady=(18, 5))
        exit_btn = tk.Button(
            exit_row, text="Exit Application", font=Theme.FONT_BUTTON,
            bg=Theme.DANGER, fg="white", activebackground="#b91c1c",
            activeforeground="white", relief="flat", bd=0,
            padx=20, pady=10, cursor="hand2", command=self.confirm_exit
        )
        exit_btn.pack(side="right")

    def _build_status_bar(self, parent):
        bar = tk.Frame(parent, bg=Theme.BG_SIDEBAR, height=28)
        bar.pack(fill="x", side="bottom")
        tk.Label(
            bar, textvariable=self.status_var, font=("Segoe UI", 9),
            bg=Theme.BG_SIDEBAR, fg=Theme.TEXT_SECONDARY, anchor="w"
        ).pack(side="left", padx=12, pady=4)

    # ------------------------------------------------------------------
    # CLOCK
    # ------------------------------------------------------------------
    def _update_clock(self):
        current_time = datetime.now().strftime("%d-%m-%Y    %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_clock)

    # ------------------------------------------------------------------
    # PROCESS LAUNCHERS
    # ------------------------------------------------------------------
    # Every button launches another script as its own process. We centralize
    # that logic in one helper so we get consistent error handling: if a
    # script is missing or crashes immediately, the user sees a clear popup
    # instead of the dashboard silently doing nothing (which is what
    # subprocess.Popen does on its own if the target file doesn't exist on
    # some platforms).
    def _launch(self, script_name, status_message):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        if not os.path.exists(script_path):
            messagebox.showerror(
                "Script Not Found",
                f"Could not find '{script_name}'.\n\n"
                f"Make sure it is in the same folder as dashboard.py."
            )
            return
        try:
            subprocess.Popen([sys.executable, script_path])
            self.status_var.set(status_message)
        except Exception as error:
            messagebox.showerror("Error", f"Failed to launch {script_name}:\n{error}")

    def register_student(self):
        self._launch("student_registration.py", "Opening student registration...")

    def capture_face(self):
        self._launch("register.py", "Opening face capture...")

    def train_model(self):
        self._launch("train.py", "Training model...")

    def mark_attendance(self):
        self._launch("attendance.py", "Starting attendance session...")

    def view_students(self):
        self._launch("view_students_gui.py", "Loading student records...")

    def view_attendance(self):
        self._launch("view_attendance_gui.py", "Loading attendance records...")

    def attendance_analytics(self):
        self._launch("attendance_analytics.py", "Loading analytics...")

    def attendance_chart(self):
        self._launch("attendance_chart.py", "Loading chart view...")

    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            self.root.destroy()


# ----------------------------------------------------------------------
# 4. ENTRY POINT
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceDashboard(root)
    root.mainloop() 