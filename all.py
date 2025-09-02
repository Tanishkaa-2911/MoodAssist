import cv2
import numpy as np
from fer import FER
import streamlit as st

# --------- Session state to remember detected mood ----------
if "detected_mood" not in st.session_state:
    st.session_state.detected_mood = None

st.subheader("📸 Detect Your Mood")
img_file = st.camera_input("Take a photo to detect your mood:")

if img_file:
    # Convert uploaded image to numpy array
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    # Initialize FER detector
    detector = FER(mtcnn=False)
    results = detector.detect_emotions(frame)

    if results:
        emotions = results[0]["emotions"]
        dominant_emotion = max(emotions, key=emotions.get)

        # Capitalize and normalize detected mood
        mood_mapping = {"Surprise": "Surprised"}  # match dataset spelling
        detected_mood = mood_mapping.get(dominant_emotion.capitalize(), dominant_emotion.capitalize())

        # Save in session state
        st.session_state.detected_mood = detected_mood

        # Show detected mood
        st.success(f"✅ Detected Mood: **{detected_mood}**")

    else:
        st.error("⚠️ No face detected! Please retake the photo.")

# --------- Redirect to Tips Page ----------
if st.session_state.detected_mood:
    if st.checkbox("✨ Show me mood improvement tips"):
        st.switch_page("pages/tips_page.py")  # No .py in deployed version
