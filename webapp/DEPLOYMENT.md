# Deploying Your Face Recognition Attendance System (Web Edition)

This adds a browser-based version of your project (`webapp/app.py`) that can
live at a public URL, alongside your existing desktop app — so your repo
shows both "built a desktop app" and "shipped it as a deployed product,"
which is the combination that reads best on a resume and in interviews.

## 1. Add the web app to your repo

In your local clone of `FaceRecognitionAttendance`:

```
mkdir webapp
```

Copy these three files (attached) into that `webapp/` folder:
- `app.py`
- `requirements.txt`
- `packages.txt`

Also copy your existing `haarcascade_frontalface_default.xml` into `webapp/`
too (Streamlit Cloud needs its own copy alongside `app.py`):

```
cp haarcascade_frontalface_default.xml webapp/
```

## 2. Push to GitHub

```
git add webapp
git commit -m "Add Streamlit web edition for live deployment"
git push
```

## 3. Deploy on Streamlit Community Cloud (free)

1. Go to **share.streamlit.io** and sign in with your GitHub account.
2. Click **New app**.
3. Pick repository `ManishYdvCodes/FaceRecognitionAttendance`, branch `main`.
4. Set **Main file path** to `webapp/app.py`.
5. Click **Deploy**. First build takes a few minutes (installing OpenCV).
6. You'll get a URL like `https://facerecognitionattendance-<random>.streamlit.app`.

## 4. Update your README

Add near the top of `README.md`:

```markdown
🔗 **Live demo:** https://your-app-url.streamlit.app
```

Interviewers and evaluators can then just click and try it — no setup,
no cloning, no "trust me it works."

## Honest caveats to know before a demo (and to mention if asked — this
actually shows engineering maturity, not weakness)

- **Storage is ephemeral on the free tier.** Registered students, trained
  models, and attendance logs persist while the app stays awake, but reset
  if it goes idle and restarts (common after ~a week of no traffic, or on
  redeploy). Fine for demoing the pipeline live; for a "real" always-on
  deployment you'd swap SQLite for a hosted DB (e.g. Supabase/Postgres) and
  images for object storage (e.g. S3) — worth mentioning in interviews as
  the "next step" you're aware of.
- **Camera capture is snapshot-based, not continuous video.** A browser
  can't give a remote server live webcam frames the way `cv2.VideoCapture`
  does locally, so registration/attendance now work by taking a photo per
  action rather than scanning a live feed. This is a legitimate, common
  pattern for browser-deployed CV apps — call it out as an intentional
  adaptation, not a bug.
- **Free tier can be slow to wake up** if no one has visited recently
  (~30-60s cold start). Worth a heads-up if you're demoing live in an
  interview — visit the link yourself a minute before you need it.

## What to say about this in an interview

"I built the core system as a desktop app with OpenCV and Tkinter, then
rebuilt the interface layer in Streamlit and deployed it so it's usable
from any browser. That meant redesigning the camera-input flow around
single-frame captures instead of continuous video, and being deliberate
about what state needs to persist versus what's fine to be ephemeral for a
demo deployment." — that's a real engineering story, not just "I made a
project."
