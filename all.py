import cv2
from fer import FER
import streamlit as st
import pandas as pd
import random
import pickle

# --------- Load trained KNN and encoders ----------
with open("knn_model.pkl", "rb") as f:
    knn = pickle.load(f)

with open("mood_encoder.pkl", "rb") as f:
    mood_encoder = pickle.load(f)

with open("interest_encoder.pkl", "rb") as f:
    interest_encoder = pickle.load(f)

# --------- Load your dataset ----------
df = pd.read_csv("CleanedDataset_Recommendation.csv")

# --------- Streamlit App ----------
st.title("😊 Mood-Based Tips Recommendation")

# Session state to remember detected mood & camera
if "detected_mood" not in st.session_state:
    st.session_state.detected_mood = None
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False

# Start Webcam
if st.button("🎥 Start Webcam"):
    st.session_state.camera_running = True
    st.session_state.detected_mood = None

# Close Webcam
if st.button("❌ Close Webcam"):
    st.session_state.camera_running = False

# Webcam detection
if st.session_state.camera_running:
    detector = FER(mtcnn=False)
    cap = cv2.VideoCapture(0)
    stframe = st.empty()

    # Mapping FER emotions to dataset moods
    mood_mapping = {
        "Surprise": "Surprised"  # Match dataset spelling
    }

    while st.session_state.camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        results = detector.detect_emotions(frame)
        if results:
            emotions = results[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)

            # Capitalize and map detected mood
            detected_mood = dominant_emotion.capitalize()
            detected_mood = mood_mapping.get(detected_mood, detected_mood)

            # Draw rectangle + label
            (x, y, w, h) = results[0]["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, detected_mood, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Save mapped mood into session state
            st.session_state.detected_mood = detected_mood

        # Show webcam in Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stframe.image(frame_rgb)

        # Exit loop if "Close Webcam" pressed
        if not st.session_state.camera_running:
            break

    cap.release()
    cv2.destroyAllWindows()

# Show detected mood after webcam is closed
if not st.session_state.camera_running and st.session_state.detected_mood:
    st.success(f"✅ Detected Mood: **{st.session_state.detected_mood}**")

# --------- Redirect to tips page ----------
if st.session_state.detected_mood:
    if st.checkbox("✨ Do you want tips for mood improvement?"):
        st.switch_page("pages/tips_page.py")
