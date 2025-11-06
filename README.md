# 🎬 Gemini Video Summarizer

An AI-powered video analysis tool that extracts keyframes, processes audio, and generates intelligent summaries using Google's Gemini AI.

## ✨ Features

- 🖼️ **Intelligent Keyframe Extraction**: Automatically identifies and extracts significant frames
- 🤖 **AI-Powered Summaries**: Generates concise video summaries using Gemini AI
- 🎵 **Audio Processing**: 
  - Extracts audio from videos
  - Generates audio narration of summaries using text-to-speech
- 📱 **User-Friendly Interface**: Built with Streamlit for easy interaction
- 💾 **Offline Support**: Works without internet for core features
- 🔄 **Format Support**: Handles MP4, MOV, AVI, and MKV video formats

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **FFmpeg**: Required for video/audio processing
   - Windows: Download from [FFmpeg Official Site](https://ffmpeg.org/download.html)
   - Add to PATH or place in one of these locations:
     - `C:\ffmpeg\bin\ffmpeg.exe`
     - `<project_root>\bin\ffmpeg.exe`
     - `%USERPROFILE%\ffmpeg\bin\ffmpeg.exe`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gemini-video-summarizer
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   - Create a `.env` file in the project root:
     ```env
     GEMINI_API_KEY=your_api_key_here
     GEMINI_MODEL=gemini-2.5-flash
     FRAME_EXTRACTION_RATE=1
     KEYFRAME_THRESHOLD=0.5
     MAX_FRAME_DIMENSION=1024
     AUDIO_EXTRACTION_ENABLED=1
     AUDIO_SAMPLE_RATE=16000
     ```

### Running the Application

1. **Activate the virtual environment** (if not already active)
   ```bash
   .\venv\Scripts\activate
   ```

2. **Start the application**
   ```bash
   streamlit run frontend/app.py
   ```

## 📁 Project Structure

```
├── config/                 # Configuration settings
├── frontend/              # Streamlit web interface
│   ├── app.py            # Main web application
│   └── temp_outputs/     # Temporary processing files
├── outputs/              # Generated outputs
│   ├── keyframes/       # Extracted video frames
│   ├── summaries/       # Generated text summaries
│   └── audio/          # Audio extractions
├── src/                  # Core processing modules
│   ├── video_processor.py    # Video processing logic
│   ├── gemini_integration.py # AI integration
│   ├── keyframe_extractor.py # Frame extraction
│   ├── audio_summary.py      # Audio processing
│   └── utils.py             # Helper utilities
└── tests/                # Unit tests
```

## 🎯 Usage

1. Open the application in your web browser
2. Upload a video file (MP4, MOV, AVI, or MKV)
3. The application will:
   - Extract and display key frames
   - Generate an AI-powered summary
   - Extract audio (if enabled)
   - Create an audio narration of the summary
4. Download or play the generated audio summary

## 🛠️ Configuration Options

- **FRAME_EXTRACTION_RATE**: Frames per second to analyze
- **KEYFRAME_THRESHOLD**: Sensitivity for keyframe detection
- **MAX_FRAME_DIMENSION**: Maximum frame size for processing
- **AUDIO_EXTRACTION_ENABLED**: Enable/disable audio processing
- **AUDIO_SAMPLE_RATE**: Audio quality setting

## 📝 License

[Your chosen license]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.