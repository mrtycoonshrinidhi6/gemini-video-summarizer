from typing import Union, List, Dict
from .keyframe_extractor import KeyframeExtractor
from .gemini_integration import GeminiIntegration
from .cloud_processor import CloudProcessor
from .utils import get_ffmpeg_path
from config.config import Config
import os
import subprocess
import whisper


class VideoProcessor:
    """
    Advanced video processor for keyframe extraction, audio transcription,
    Gemini summary generation, and optional cloud upload.
    """

    def __init__(self, use_cloud: bool = False):
        # Core modules
        self.keyframe_extractor = KeyframeExtractor()
        self.gemini_integration = GeminiIntegration()
        self.cloud_processor = CloudProcessor() if use_cloud else None

        # Whisper model for audio → text
        self.whisper_model = whisper.load_model("base")

    # ----------------------------------------------------------
    # MAIN PROCESS FUNCTION
    # ----------------------------------------------------------
    def process_video(self, video_path: str, video_description: str = "") -> Dict[str, Union[List[str], str, None]]:
        """
        Process video to extract keyframes, audio, transcription, and AI summary.
        Returns dict containing paths and text outputs.
        """
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = None
        transcription_text = ""
        summary = ""
        summary_path = ""

        # ----------------------------------------------------------
        # 1️⃣ AUDIO EXTRACTION
        # ----------------------------------------------------------
        if Config.AUDIO_EXTRACTION_ENABLED:
            audio_path = os.path.join(Config.AUDIO_DIR, f"{video_name}.wav")
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)

            try:
                FFMPEG_PATH = get_ffmpeg_path()
            except FileNotFoundError:
                FFMPEG_PATH = "ffmpeg"

            try:
                cmd = [
                    FFMPEG_PATH, "-y", "-i", video_path,
                    "-ar", str(Config.AUDIO_SAMPLE_RATE),
                    "-ac", "1", audio_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print(f"✅ Audio extracted successfully: {audio_path}")
            except Exception as e:
                print(f"⚠️ Error extracting audio: {e}")
                audio_path = None

        # ----------------------------------------------------------
        # 2️⃣ KEYFRAME EXTRACTION
        # ----------------------------------------------------------
        keyframes = self.keyframe_extractor.extract_keyframes(video_path)
        keyframe_paths = self.keyframe_extractor.save_keyframes(keyframes, video_name)

        # ----------------------------------------------------------
        # 3️⃣ AUDIO → TEXT (TRANSCRIPTION)
        # ----------------------------------------------------------
        if audio_path and os.path.exists(audio_path):
            try:
                print("🎧 Transcribing audio...")
                result = self.whisper_model.transcribe(audio_path)
                transcription_text = result.get("text", "").strip()
                print("✅ Audio transcription complete.")
            except Exception as e:
                print(f"⚠️ Whisper transcription failed: {e}")

        # ----------------------------------------------------------
        # 4️⃣ GENERATE AI SUMMARY
        # ----------------------------------------------------------
        if transcription_text:
            summary = self.generate_summary_from_text(transcription_text, video_description)
        else:
            summary = self.gemini_integration.generate_summary(keyframe_paths, video_description)

        # Save summary file
        summary_path = self.gemini_integration.save_summary(summary, video_name)

        # ----------------------------------------------------------
        # 5️⃣ OPTIONAL CLOUD UPLOAD
        # ----------------------------------------------------------
        if self.cloud_processor:
            for path in keyframe_paths:
                self.cloud_processor.upload_file(path, f"keyframes/{os.path.basename(path)}")
            self.cloud_processor.upload_file(summary_path, f"summaries/{os.path.basename(summary_path)}")
            if audio_path:
                self.cloud_processor.upload_file(audio_path, f"audio/{os.path.basename(audio_path)}")

        # ----------------------------------------------------------
        # ✅ RETURN RESULTS
        # ----------------------------------------------------------
        return {
            "keyframes": keyframe_paths,
            "summary": summary,
            "summary_path": summary_path,
            "audio_path": audio_path,
            "transcription": transcription_text
        }

    # ----------------------------------------------------------
    # HELPER: SUMMARIZE FROM TRANSCRIPTION TEXT
    # ----------------------------------------------------------
    def generate_summary_from_text(self, text: str, description: str = "") -> str:
        """
        Uses Google Gemini to summarize a transcription into clean bullet points.
        """
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        prompt = (
            f"Summarize the following video transcription in clear, structured bullet points.\n"
            f"Context: {description}\n\n"
            f"Transcription:\n{text}"
        )

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text or "No summary generated."
        except Exception as e:
            print(f"⚠️ Gemini summarization failed: {e}")
            return "Error generating summary."

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes audio to text using Whisper model.
        Returns the transcribed text.
        """
        try:
            print(f"🎧 Transcribing audio file: {audio_path}")
            result = self.whisper_model.transcribe(audio_path)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"⚠️ Audio transcription failed: {e}")
            return ""