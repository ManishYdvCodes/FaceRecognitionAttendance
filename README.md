# Face Recognition Attendance System

A desktop attendance system built with **Python, OpenCV, and Tkinter**. Students are registered with a webcam face capture, a local LBPH model is trained on the captured faces, and attendance is marked automatically via live face recognition — logged to CSV and viewable through a built‑in GUI, with basic analytics and charts.

## Features

- **Student Registration** — Tkinter form to capture Student ID/Name and grab face samples from the webcam (Haar Cascade face detection).
- **Model Training** — Trains an OpenCV LBPH face recognizer on the captured dataset.
- **Automated Attendance** — Live webcam recognition marks attendance and logs it to a daily CSV file.
- **Attendance Viewer** — GUI table to browse attendance by date, with record counts and refresh.
- **Analytics Dashboard** — Quick summary of total vs. present students.
- **Attendance Charts** — Visual breakdown of attendance using Matplotlib.
- **SQLite Student Database** — Stores student records (ID, name, department, year).
- **Central Dashboard** — Single launcher window that opens every module.

## Tech Stack

| Layer          | Tool                          |
|----------------|--------------------------------|
| GUI            | Tkinter                        |
| Face Detection | OpenCV Haar Cascade            |
| Face Recognition | OpenCV LBPH (`cv2.face`)     |
| Database       | SQLite3                        |
| Data / Charts  | pandas, matplotlib             |
| Images         | Pillow (PIL)                   |

## Project Structure

```
FaceRecognitionAttendance/
├── main_dashboard.py           # Central launcher GUI
├── register.py                 # Face capture / registration GUI
├── student_registration.py     # Student DB entry form
├── train.py                    # Trains the LBPH recognizer on dataset/
├── attendance.py                # Live recognition + attendance logging
├── attendance_analytics.py     # Summary stats GUI
├── attendance_chart.py         # Matplotlib attendance chart
├── view_attendance_gui.py      # Attendance records viewer
├── view_students_gui.py        # Registered students viewer
├── view_student.py             # CLI: print all students
├── add_student.py              # CLI: quick sample insert (dev/testing)
├── database.py                 # Creates the students table
├── haarcascade_frontalface_default.xml
├── requirements.txt
└── .gitignore
```

> `dataset/` (captured face images), `trainer/` (trained model), and `attendance/` (CSV logs) are generated at runtime and are git-ignored.

## Installation

```bash
git clone https://github.com/ManishYdvCodes/FaceRecognitionAttendance.git
cd FaceRecognitionAttendance
pip install -r requirements.txt
```

## Usage

1. **Initialize the database**
   ```bash
   python database.py
   ```
2. **Launch the dashboard**
   ```bash
   python main_dashboard.py
   ```
3. From the dashboard:
   - **Register Student** → enter details and capture face samples via webcam.
   - **Train Model** → builds the recognizer from all captured faces.
   - **Mark Attendance** → runs live recognition and logs attendance to CSV.
   - **View Attendance / Students** → browse records in-app.
   - **Analytics / Charts** → see attendance summaries.

## Requirements

- Python 3.9+
- A webcam
- See `requirements.txt` for Python packages

## Known Limitations / Roadmap

- LBPH is a lightweight recognizer — accuracy drops with poor lighting or large student counts; a deep-learning-based recognizer (e.g. `face_recognition` / dlib or a CNN embedding model) would scale better.
- No authentication/login on the dashboard.
- Attendance is stored as daily CSVs rather than in the database — could be unified into SQLite.
- No automated tests yet.

## Author

**Manish Yadav**

## License

Released under the [MIT License](LICENSE).
