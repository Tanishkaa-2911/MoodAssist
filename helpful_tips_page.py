import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# ---------------- Function to Generate PDF ----------------
def generate_mood_report(username, detected_mood, interest, confidence_score, recommendations, helpful_tips):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Logo
    try:
        logo_path = "mood-tips-logo.png"
        logo = ImageReader(logo_path)
        c.drawImage(logo, 20, height - 90, width=50, height=50, mask='auto')
    except:
        pass

    # Title
    highlight_height = 40
    highlight_width = 420
    highlight_x = (width - highlight_width) / 2
    highlight_y = height - 80
    c.setFillColor(colors.HexColor("#893A3A"))
    c.roundRect(highlight_x, highlight_y, highlight_width, highlight_height, 10, fill=1)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.white)
    c.drawCentredString(width / 2, highlight_y + 12, "🧠 Mood Analysis Report 📊")
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, highlight_y - 20, "Your Personalized Emotional Insights")

    report_time = datetime.now().strftime("%d %B %Y | %I:%M %p")

    # User Details
    c.setFont("Times-Roman", 12)
    c.setFillColor(colors.black)
    c.drawString(50, height - 140, f"User: {username}")
    c.drawString(50, height - 160, f"Detected Mood: {detected_mood}")
    c.drawString(50, height - 180, f"Interest: {interest}")
    c.drawString(50, height - 200, f"Model Confidence: {confidence_score}%")
    c.drawString(width - c.stringWidth(f"Report Generated: {report_time}", "Helvetica", 12) - 40, 40,
                 f"Report Generated: {report_time}")

    # Recommended Tips
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 240, "Recommended Tips:")
    c.setFont("Helvetica", 12)
    y = height - 260
    for i, tip in enumerate(recommendations, start=1):
        c.drawString(60, y, f"{i}. {tip}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50

    # Helpful Tips Section
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "✪ Tips You Found Helpful:")
    y -= 20
    c.setFont("Helvetica", 12)
    if helpful_tips:
        for i, tip in enumerate(helpful_tips, start=1):
            c.drawString(60, y, f"{i}. {tip}")
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
    else:
        c.drawString(60, y, "No tips marked as helpful.")

    c.save()
    buffer.seek(0)
    return buffer

# ---------------- Main Page ----------------
st.set_page_config(page_title="Helpful Tips Report", layout="centered")
st.title("📄 Download Your Personalized Mood Report")

# ✅ Check required session variables
required_keys = ["username", "detected_mood", "selected_interest", "confidence_score", "recommendations"]
if all(key in st.session_state for key in required_keys):

    username = st.session_state["username"]
    detected_mood = st.session_state["detected_mood"]
    selected_interest = st.session_state["selected_interest"]
    confidence_score = st.session_state["confidence_score"]
    recommendations = st.session_state["recommendations"]
    helpful_tips = st.session_state.get("helpful_tips", [])

    # ✅ Generate PDF buffer
    pdf_buffer = generate_mood_report(
        username=username,
        detected_mood=detected_mood,
        interest=selected_interest,
        confidence_score=confidence_score,
        recommendations=recommendations,
        helpful_tips=helpful_tips
    )

    # ✅ Download Button
    if st.download_button(
        label="📥 Download Your Mood Report",
        data=pdf_buffer,
        file_name=f"{username}_mood_report.pdf",
        mime="application/pdf"
    ):
        # Save logs
        log_file = "user_logs.csv"
        username_clean = username.strip() if username else "Anonymous"
        data_row = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d"),
            "User": username_clean,
            "Mood": detected_mood,
            "Interest": selected_interest,
            "Confidence": confidence_score,
            "Helpful_Tips": "; ".join(helpful_tips) if helpful_tips else "None"
        }
        new_row_df = pd.DataFrame([data_row])
        if os.path.exists(log_file):
            df_logs = pd.read_csv(log_file)
            df_logs = pd.concat([df_logs, new_row_df], ignore_index=True)
            df_logs = df_logs.drop_duplicates()
        else:
            df_logs = new_row_df
        df_logs.to_csv(log_file, index=False)

else:
    st.error("⚠️ Missing data! Please detect mood and select tips on the Tips Page first.")
