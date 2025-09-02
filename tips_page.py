import streamlit as st
import random
import pandas as pd
import pickle

# --------- Load trained KNN and encoders ---------
with open("knn_model.pkl", "rb") as f:
    knn = pickle.load(f)
with open("mood_encoder.pkl", "rb") as f:
    mood_encoder = pickle.load(f)
with open("interest_encoder.pkl", "rb") as f:
    interest_encoder = pickle.load(f)

# --------- Load dataset ---------
df = pd.read_csv("CleanedDataset_Recommendation.csv")

st.set_page_config(page_title="Mood Tips & Report", layout="centered")
st.title("💡 Mood Improvement Tips & Report")

# --------- Main App ---------
if "detected_mood" in st.session_state and st.session_state.detected_mood:
    mood = st.session_state.detected_mood
    st.success(f"✅ Your Detected Mood: **{mood}**")

    # Take username
    username = st.text_input("Enter your name:")
    if username:
        st.session_state["username"] = username

    # Select interest
    selected_interest = st.selectbox("🎯 Select your Interest", df['Interest'].unique())
    st.session_state["selected_interest"] = selected_interest

    # Slider for number of tips
    n_tips = st.slider("🔢 Number of Tips to Show", min_value=1, max_value=10, value=3)

    # --------- Recommendation Function ---------
    def recommend_tips(mood, interest, n_tips=3):
        try:
            encoded_mood = mood_encoder.transform([mood])[0]
            encoded_interest = interest_encoder.transform([interest])[0]
            n_neighbors = min(len(df), knn.n_samples_fit_)
            distances, indices = knn.kneighbors([[encoded_mood, encoded_interest]], n_neighbors=n_neighbors)
            nearest_distance = distances[0][0]
            confidence = max(0, 1 - nearest_distance)
            confidence_percent = round(confidence * 100, 2)
            all_recs = df.iloc[indices[0]]
            filtered_recs = all_recs[all_recs["Interest"] == interest]['Recommendation'].tolist()
            if len(filtered_recs) < n_tips:
                mood_recs = df[df["Mood"] == mood]['Recommendation'].tolist()
                filtered_recs.extend(mood_recs)
            filtered_recs = list(dict.fromkeys(filtered_recs))
            recs = random.sample(filtered_recs, k=min(n_tips, len(filtered_recs)))
            return recs, confidence_percent
        except Exception as e:
            return [f"Error: {e}"], 0

    # Generate & Cache Recommendations
    if "recommendations" not in st.session_state:
        st.session_state.recommendations, st.session_state.confidence_score = recommend_tips(
            mood, selected_interest, n_tips
        )

    # Regenerate recommendations if interest or tip count changes
    if st.session_state.get("prev_interest") != selected_interest or st.session_state.get("prev_n_tips") != n_tips:
        st.session_state.recommendations, st.session_state.confidence_score = recommend_tips(
            mood, selected_interest, n_tips
        )

    st.session_state.prev_interest = selected_interest
    st.session_state.prev_n_tips = n_tips

    # Save recommendations & confidence score in session
    recommendations = st.session_state.recommendations
    st.session_state["recommendations"] = recommendations
    confidence_score = st.session_state.confidence_score
    st.session_state["confidence_score"] = confidence_score

    # --------- Show Confidence ---------
    st.write(f"**Model Confidence Score:** {confidence_score}%")

    # --------- Helpful Tips ---------
    st.subheader("✨ Recommended Tips:")
    if "helpful_tips" not in st.session_state:
        st.session_state.helpful_tips = []

    for tip in recommendations:
        checked = tip in st.session_state.helpful_tips
        if st.checkbox(f"{tip}", value=checked, key=f"tip_{tip}"):
            if tip not in st.session_state.helpful_tips:
                st.session_state.helpful_tips.append(tip)
        else:
            if tip in st.session_state.helpful_tips:
                st.session_state.helpful_tips.remove(tip)

    # --------- Button to Go to Helpful Tips Page ---------
    if st.button("📄 Generate & Download Mood Report"):
        st.switch_page("pages/helpful_tips_page.py")

else:
    st.error("⚠️ No mood detected yet. Please go back and detect your mood first.")
