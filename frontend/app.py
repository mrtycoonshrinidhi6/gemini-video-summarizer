import streamlit as st
import os
import tempfile
import subprocess
import time
import speech_recognition as sr
import glob
import shutil

# --- Page Configuration ---
st.set_page_config(page_title="🎥 AI Video Summarizer", layout="wide")

st.title("🎬 AI Video Summarizer (Offline + Keyframes)")
st.markdown("Upload a video to extract **key frames**, audio, transcribe it, and download the **text summary**.")

# --- Helper Functions ---

def extract_keyframes(video_path, interval_sec, max_frames_to_display):
    """Extracts key frames from video using ffmpeg at a given interval"""
    print("  [INFO] Extracting key frames...")
    st.info("Extracting key frames...")
    
    keyframe_dir = tempfile.mkdtemp()
    frame_paths = []
    
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps=1/{interval_sec}",
        "-vsync", "vfr",
        f"{keyframe_dir}/frame-%04d.png"
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("  [SUCCESS] Key frame extraction complete.")
        frame_paths = sorted(glob.glob(f"{keyframe_dir}/*.png"))
        
        if not frame_paths:
            st.warning("No key frames were extracted. The video might be shorter than the interval.")
            return keyframe_dir, []

        st.subheader("🖼️ Extracted Key Frames")
        frames_to_show = frame_paths[:max_frames_to_display]
        num_columns = 5
        cols = st.columns(num_columns)
        
        for i, frame_path in enumerate(frames_to_show):
            with cols[i % num_columns]:
                st.image(frame_path, use_column_width=True, caption=f"Frame {i+1}")
        
        if len(frame_paths) > max_frames_to_display:
            st.text(f"...and {len(frame_paths) - max_frames_to_display} more frames (not shown).")
            
        return keyframe_dir, frame_paths
        
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] FFMPEG (keyframes) failed: {e.stderr.decode()}")
        st.error(f"FFMPEG Error (Keyframes): {e.stderr.decode()}. Please ensure FFMPEG is installed.")
        return keyframe_dir, []


def extract_audio(video_path):
    """Extracts audio from video using ffmpeg"""
    print("  [INFO] Extracting audio...")
    st.info("Extracting audio from video...")
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("  [SUCCESS] Audio extraction complete.")
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] FFMPEG (audio) failed: {e.stderr.decode()}")
        st.error(f"FFMPEG Error (Audio): {e.stderr.decode()}. Please ensure FFMPEG is installed.")
        return None


def transcribe_audio(audio_path):
    """Transcribes audio to text using SpeechRecognition (offline CMU Sphinx fallback)"""
    print("  [INFO] Transcribing audio...")
    st.info("Transcribing audio... This may take a moment.")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    
    text = ""
    try:
        print("    [Attempt] Trying Google Speech Recognition (Online)...")
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("    [WARN] Google Speech Recognition could not understand audio.")
        st.warning("Google Speech Recognition could not understand audio. Trying offline fallback...")
    except sr.RequestError as e:
        print(f"    [WARN] Could not request results from Google; {e}. Trying offline fallback...")
        st.warning(f"Could not connect to Google Speech Recognition. Trying offline fallback...")
    
    if not text:
        try:
            print("    [Attempt] Trying CMU Sphinx (Offline)...")
            text = recognizer.recognize_sphinx(audio)
            print("  [SUCCESS] Transcription complete (Offline).")
        except sr.UnknownValueError:
            print("  [ERROR] Sphinx could not understand audio.")
            st.error("Offline transcription (Sphinx) could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"  [ERROR] Sphinx error: {e}")
            st.error(f"Offline transcription (Sphinx) error: {e}")
            return None
            
    print("  [SUCCESS] Transcription complete.")
    return text


# --- Main Application ---

uploaded_file = st.file_uploader("📂 Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
        tmpfile.write(uploaded_file.read())
        temp_video_path = tmpfile.name
    
    st.video(temp_video_path)
    
    st.sidebar.subheader("⚙️ Processing Options")
    keyframe_interval = st.sidebar.slider("Keyframe Interval (seconds)", 1, 60, 10)
    max_frames = st.sidebar.slider("Max Keyframes to Display", 5, 50, 10)
    
    progress_bar = st.progress(0, text="Starting process...")
    print("\n--- New Video Uploaded. Starting Process ---")

    audio_path = None
    keyframe_dir = None

    try:
        # 1. Extract Key Frames
        print("--- Step 1: Extracting Key Frames ---")
        keyframe_dir, keyframes = extract_keyframes(temp_video_path, keyframe_interval, max_frames)
        
        if keyframe_dir:
            st.success("✅ Key frame extraction step complete.")
            progress_bar.progress(20, text="Key Frames Extracted.")

        # 2. Extract Audio
        st.subheader("🔊 Step 2: Extracting Audio")
        print("--- Step 2: Extracting Audio ---")
        audio_path = extract_audio(temp_video_path)
        
        if audio_path:
            st.success("✅ Audio extracted successfully.")
            progress_bar.progress(40, text="Audio Extracted.")

            # 3. Transcribe Audio → Text
            st.subheader("🗣️ Step 3: Transcribing Audio to Text")
            print("--- Step 3: Transcribing Audio to Text ---")
            transcription = transcribe_audio(audio_path)
            
            if transcription:
                st.text_area("📝 Transcribed Text", transcription, height=200)
                st.success("✅ Transcription complete.")
                progress_bar.progress(80, text="Transcription Complete.")

                # ✅ NEW: Add Download Button for Transcription (or all summaries)
                st.subheader("⬇️ Step 4: Download Your Summary / Transcription")
                download_content = f"🎬 Video Summary\n\n🗣️ Transcription:\n{transcription}\n\n"
                st.download_button(
                    label="⬇️ Download Full Summary Report",
                    data=download_content,
                    file_name="video_summary_report.txt",
                    mime="text/plain",
                )
                progress_bar.progress(100, text="Process Complete!")
                st.success("🎉 All steps completed successfully!")
            else:
                st.error("Failed to transcribe audio.")
                progress_bar.progress(100, text="Error during transcription.")
                print("--- Process failed at transcription step. ---")
                
        else:
            st.error("Failed to extract audio. Cannot proceed with transcription/summary.")
            progress_bar.progress(100, text="Error during audio extraction.")
            print("--- Process failed at audio extraction step. ---")
            
    finally:
        print("--- Cleaning up temporary files... ---")
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            print(f"  Removed: {temp_video_path}")
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"  Removed: {audio_path}")
        if keyframe_dir and os.path.exists(keyframe_dir):
            shutil.rmtree(keyframe_dir)
            print(f"  Removed keyframe directory: {keyframe_dir}")
        print("--- Cleanup complete. ---")

else: 
    st.info("👆 Upload a video to get started!")
