import os
import sqlite3
from datetime import datetime, date
from zoneinfo import ZoneInfo

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Config / paths
# --------------------------------------------------------------------------
DB_PATH = "students.db"
DATASET_DIR = "dataset"
TRAINER_DIR = "trainer"
TRAINER_PATH = os.path.join(TRAINER_DIR, "trainer.yml")
ATTENDANCE_DIR = "attendance"
CASCADE_PATH = "haarcascade_frontalface_default.xml"
IST = ZoneInfo("Asia/Kolkata")
DUPLICATE_THRESHOLD = 60
RECOGNITION_THRESHOLD = 60
SAMPLES_TARGET = 20  # fewer than the desktop version's 50, since each
                      # sample here is a deliberate browser photo, not a
                      # free-running video frame

st.set_page_config(
    page_title="Face Recognition Attendance",
    page_icon="🎓",
    layout="wide",
)

for d in (DATASET_DIR, TRAINER_DIR, ATTENDANCE_DIR):
    os.makedirs(d, exist_ok=True)


# --------------------------------------------------------------------------
# Database helpers
# --------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            year TEXT
        )"""
    )
    conn.commit()
    return conn


def get_students_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY id", conn)
    conn.close()
    return df


def student_name(student_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM students WHERE id=?", (student_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "Unknown"


# --------------------------------------------------------------------------
# Face detection / recognition helpers
# --------------------------------------------------------------------------
@st.cache_resource
def get_face_detector():
    return cv2.CascadeClassifier(CASCADE_PATH)


def detect_largest_face(gray_img):
    detector = get_face_detector()
    faces = detector.detectMultiScale(gray_img, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        return None
    # pick the largest detected face box
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return x, y, w, h


def detect_all_faces(gray_img):
    detector = get_face_detector()
    return detector.detectMultiScale(gray_img, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))


def load_recognizer():
    if not os.path.exists(TRAINER_PATH):
        return None
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)
    return recognizer


def check_duplicate_face(gray_face, new_student_id):
    """Mirrors the desktop app's duplicate-face guard during registration."""
    recognizer = load_recognizer()
    if recognizer is None:
        return False, None, None
    predicted_id, confidence = recognizer.predict(gray_face)
    if confidence < DUPLICATE_THRESHOLD and str(predicted_id) != str(new_student_id):
        return True, predicted_id, student_name(predicted_id)
    return False, None, None


def pil_to_gray(image: Image.Image):
    arr = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return bgr, gray


def next_sample_index(student_id):
    existing = [f for f in os.listdir(DATASET_DIR) if f.startswith(f"User.{student_id}.")]
    return len(existing) + 1


def sample_count(student_id):
    return len([f for f in os.listdir(DATASET_DIR) if f.startswith(f"User.{student_id}.")])


# --------------------------------------------------------------------------
# Attendance helpers
# --------------------------------------------------------------------------
def today_attendance_path(day=None):
    day = day or datetime.now(IST)
    return os.path.join(ATTENDANCE_DIR, f"Attendance_{day.strftime('%Y_%m_%d')}.csv")


def load_attendance(day=None):
    path = today_attendance_path(day)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["ID", "Name", "Time"])


def mark_attendance(student_id, name):
    path = today_attendance_path()
    df = load_attendance()
    if student_id in df["ID"].values:
        return False  # already marked today
    new_row = pd.DataFrame([[student_id, name, datetime.now(IST).strftime("%H:%M:%S")]],
                            columns=["ID", "Name", "Time"])
    combined = pd.concat([df, new_row], ignore_index=True)
    combined.to_csv(path, index=False)
    return True


def list_attendance_dates():
    files = [f for f in os.listdir(ATTENDANCE_DIR) if f.startswith("Attendance_") and f.endswith(".csv")]
    dates = []
    for f in files:
        try:
            d = datetime.strptime(f[len("Attendance_"):-4], "%Y_%m_%d").date()
            dates.append(d)
        except ValueError:
            continue
    return sorted(dates, reverse=True)


# --------------------------------------------------------------------------
# Sidebar navigation
# --------------------------------------------------------------------------
st.sidebar.title("🎓 Attendance System")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Register Student", "Capture Face Samples", "Train Model",
     "Mark Attendance", "View Attendance", "View Students", "Analytics"],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Free-tier hosting uses temporary storage — registered faces and "
    "attendance reset if the app goes idle and restarts. Great for a live "
    "demo; add a persistent DB for production use."
)

# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------
if page == "Dashboard":
    st.title("Face Recognition Attendance System")
    st.caption("Web edition — OpenCV LBPH + Haar Cascade, running through your browser camera.")

    students_df = get_students_df()
    today_df = load_attendance()
    model_ready = os.path.exists(TRAINER_PATH)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Students", len(students_df))
    c2.metric("Present Today", len(today_df))
    c3.metric("Model Status", "Trained ✅" if model_ready else "Not Trained ⚠️")
    c4.metric("Attendance Rate Today", f"{(len(today_df)/len(students_df)*100):.0f}%" if len(students_df) else "—")

    st.markdown("### How this works")
    st.markdown(
        "1. **Register Student** — add their ID, name, department, year.\n"
        "2. **Capture Face Samples** — take a series of photos via your camera.\n"
        "3. **Train Model** — builds the recognizer from every registered face.\n"
        "4. **Mark Attendance** — take a photo; recognized students get logged automatically.\n"
        "5. **View Attendance / Analytics** — browse and chart the results."
    )

# --------------------------------------------------------------------------
# Register Student
# --------------------------------------------------------------------------
elif page == "Register Student":
    st.title("Register Student")
    st.caption("Add a student record. Do this before capturing face samples for them.")

    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        student_id = col1.text_input("Student ID (numeric)")
        name = col2.text_input("Name")
        department = col1.text_input("Department")
        year = col2.text_input("Year")
        submitted = st.form_submit_button("Register Student")

    if submitted:
        if not student_id.strip().isdigit():
            st.error("Student ID must be numeric — it's used as the face-recognition label.")
        elif not name.strip():
            st.error("Name is required.")
        else:
            try:
                conn = get_conn()
                conn.execute(
                    "INSERT INTO students (id, name, department, year) VALUES (?, ?, ?, ?)",
                    (int(student_id), name.strip(), department.strip(), year.strip()),
                )
                conn.commit()
                conn.close()
                st.success(f"Registered {name} (ID {student_id}). Now go to 'Capture Face Samples'.")
            except sqlite3.IntegrityError:
                st.error(f"A student with ID {student_id} already exists.")

    st.markdown("### Currently Registered")
    st.dataframe(get_students_df(), use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# Capture Face Samples
# --------------------------------------------------------------------------
elif page == "Capture Face Samples":
    st.title("Capture Face Samples")

    students_df = get_students_df()
    if students_df.empty:
        st.warning("No students registered yet. Go to 'Register Student' first.")
    else:
        options = {f"{row.id} — {row.name}": row.id for row in students_df.itertuples()}
        chosen = st.selectbox("Select student", list(options.keys()))
        student_id = options[chosen]

        count = sample_count(student_id)
        st.progress(min(count / SAMPLES_TARGET, 1.0))
        st.write(f"Samples captured for this student: **{count} / {SAMPLES_TARGET}**")

        img_file = st.camera_input("Take a photo (vary angle/expression slightly between shots)")

        if img_file is not None:
            image = Image.open(img_file)
            bgr, gray = pil_to_gray(image)
            box = detect_largest_face(gray)

            if box is None:
                st.error("No face detected in that shot — try better lighting or move closer.")
            else:
                x, y, w, h = box
                face = gray[y:y + h, x:x + w]

                is_dup, existing_id, existing_name = check_duplicate_face(face, student_id)
                if is_dup:
                    st.error(
                        f"This face is already registered as ID {existing_id} ({existing_name}). "
                        "Each face can only be registered under one student ID."
                    )
                else:
                    idx = next_sample_index(student_id)
                    cv2.imwrite(os.path.join(DATASET_DIR, f"User.{student_id}.{idx}.jpg"), face)
                    st.success(f"Sample #{idx} saved for {student_name(student_id)}.")
                    st.image(face, caption="Captured face (grayscale, as stored)", width=150)
                    st.rerun()

        if count >= SAMPLES_TARGET:
            st.info("You have enough samples for this student. Head to 'Train Model' when ready.")

# --------------------------------------------------------------------------
# Train Model
# --------------------------------------------------------------------------
elif page == "Train Model":
    st.title("Train Model")
    st.caption("Builds the LBPH face recognizer from every sample in the dataset.")

    total_samples = len([f for f in os.listdir(DATASET_DIR) if f.lower().endswith(".jpg")])
    student_ids = sorted({f.split(".")[1] for f in os.listdir(DATASET_DIR) if f.lower().endswith(".jpg")})

    st.write(f"Dataset: **{total_samples} images** across **{len(student_ids)} students**.")

    if st.button("Train Model", type="primary", disabled=(total_samples == 0)):
        with st.spinner("Training LBPH recognizer..."):
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            faces, ids = [], []
            for fname in os.listdir(DATASET_DIR):
                if not fname.lower().endswith(".jpg"):
                    continue
                img_path = os.path.join(DATASET_DIR, fname)
                face_img = Image.open(img_path).convert("L")
                faces.append(np.array(face_img, "uint8"))
                ids.append(int(fname.split(".")[1]))
            recognizer.train(faces, np.array(ids))
            recognizer.save(TRAINER_PATH)
        st.success(f"Training complete — model trained on {len(faces)} images from {len(set(ids))} students.")

    if total_samples == 0:
        st.warning("No face samples yet. Capture samples first.")

# --------------------------------------------------------------------------
# Mark Attendance
# --------------------------------------------------------------------------
elif page == "Mark Attendance":
    st.title("Mark Attendance")

    if not os.path.exists(TRAINER_PATH):
        st.warning("Model isn't trained yet. Go to 'Train Model' first.")
    else:
        recognizer = load_recognizer()
        img_file = st.camera_input("Take a photo to mark attendance (one or more faces)")

        if img_file is not None:
            image = Image.open(img_file)
            bgr, gray = pil_to_gray(image)
            faces = detect_all_faces(gray)

            if len(faces) == 0:
                st.error("No face detected. Try again with better lighting / framing.")
            else:
                marked_this_round = []
                for (x, y, w, h) in faces:
                    id_, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                    if confidence < RECOGNITION_THRESHOLD:
                        name = student_name(id_)
                        was_new = mark_attendance(id_, name)
                        color = (0, 200, 0)
                        label = f"{name}{' (already marked)' if not was_new else ''}"
                        if was_new:
                            marked_this_round.append(name)
                    else:
                        label = "Unknown"
                        color = (0, 0, 220)
                    cv2.rectangle(bgr, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(bgr, label, (x, max(y - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                st.image(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), caption="Recognition result", use_container_width=True)

                if marked_this_round:
                    st.success(f"Attendance marked for: {', '.join(marked_this_round)}")
                else:
                    st.info("No new attendance marked (already marked today, or face not recognized).")

        st.markdown("### Today's Attendance So Far")
        st.dataframe(load_attendance(), use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# View Attendance
# --------------------------------------------------------------------------
elif page == "View Attendance":
    st.title("View Attendance")

    dates = list_attendance_dates()
    if not dates:
        st.info("No attendance recorded yet.")
    else:
        chosen_date = st.selectbox("Select date", dates, format_func=lambda d: d.strftime("%d %b %Y"))
        df = load_attendance(datetime.combine(chosen_date, datetime.min.time()))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"Attendance_{chosen_date.strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
        )

# --------------------------------------------------------------------------
# View Students
# --------------------------------------------------------------------------
elif page == "View Students":
    st.title("Registered Students")
    df = get_students_df()
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.markdown("### Remove a Student")
        options = {f"{row.id} — {row.name}": row.id for row in df.itertuples()}
        chosen = st.selectbox("Select student to remove", list(options.keys()))
        if st.button("Delete Student", type="secondary"):
            sid = options[chosen]
            conn = get_conn()
            conn.execute("DELETE FROM students WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            for f in os.listdir(DATASET_DIR):
                if f.startswith(f"User.{sid}."):
                    os.remove(os.path.join(DATASET_DIR, f))
            st.success("Student and their face samples removed. Retrain the model to apply the change.")
            st.rerun()

# --------------------------------------------------------------------------
# Analytics
# --------------------------------------------------------------------------
elif page == "Analytics":
    st.title("Attendance Analytics")

    students_df = get_students_df()
    total_students = len(students_df)
    today_df = load_attendance()
    present = len(today_df)
    absent = max(total_students - present, 0)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Today's Attendance")
        if total_students > 0:
            fig, ax = plt.subplots()
            ax.pie([present, absent], labels=["Present", "Absent"], autopct="%1.1f%%",
                   colors=["#22c55e", "#ef4444"])
            ax.set_title("Attendance Analysis")
            st.pyplot(fig)
        else:
            st.info("Register students to see analytics.")

    with c2:
        st.markdown("#### Attendance Over Last 7 Days")
        dates = list_attendance_dates()[:7]
        if dates:
            counts = [len(load_attendance(datetime.combine(d, datetime.min.time()))) for d in dates]
            fig2, ax2 = plt.subplots()
            ax2.bar([d.strftime("%d %b") for d in reversed(dates)], list(reversed(counts)), color="#3b82f6")
            ax2.set_ylabel("Students Present")
            st.pyplot(fig2)
        else:
            st.info("No attendance history yet.")
