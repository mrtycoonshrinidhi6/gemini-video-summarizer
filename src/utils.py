import os
import shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from typing import List, Union
from tqdm import tqdm
from config.config import Config
import ffmpeg


def get_ffmpeg_path() -> str:
    """Return a valid ffmpeg executable path even if it's not in PATH.

    Tries shutil.which first, then a couple of sensible Windows/local fallbacks.
    Raises FileNotFoundError if no ffmpeg binary is found.
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    possible_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        str(Path(__file__).parent / "bin" / "ffmpeg.exe"),
        str(Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe"),
    ]
    for p in possible_paths:
        if Path(p).exists():
            return p

    raise FileNotFoundError("FFmpeg not found. Please install or add to PATH.")

def validate_video_file(video_path: str) -> bool:
    """
    Validate that the video file exists and is readable.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        cap.release()
        return True
    except Exception as e:
        print(f"Error validating video file: {e}")
        return False

def get_video_metadata(video_path: str) -> dict:
    """
    Extract basic metadata from a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        dict: Dictionary containing video metadata
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), 
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found in file")
            
        return {
            'duration': float(video_stream.get('duration', 0)),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'fps': eval(video_stream.get('avg_frame_rate', '0/1')),
            'codec': video_stream.get('codec_name', 'unknown'),
            'format': probe.get('format', {}).get('format_name', 'unknown')
        }
    except Exception as e:
        print(f"Error extracting video metadata: {e}")
        return {}

def resize_frame(frame: np.ndarray, max_dimension: int = 1024) -> np.ndarray:
    """
    Resize a frame while maintaining aspect ratio.
    
    Args:
        frame: Input frame as numpy array
        max_dimension: Maximum width or height dimension
        
    Returns:
        np.ndarray: Resized frame
    """
    h, w = frame.shape[:2]
    if max(h, w) <= max_dimension:
        return frame
        
    if h > w:
        new_h = max_dimension
        new_w = int(w * (max_dimension / h))
    else:
        new_w = max_dimension
        new_h = int(h * (max_dimension / w))
        
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

def frames_to_video(frames: List[np.ndarray], output_path: str, fps: int = 30) -> str:
    """
    Convert a list of frames to a video file.
    
    Args:
        frames: List of frames as numpy arrays
        output_path: Path to save the output video
        fps: Frames per second for output video
        
    Returns:
        str: Path to the generated video
    """
    if not frames:
        raise ValueError("No frames provided for video creation")
        
    height, width = frames[0].shape[:2]
    os.makedirs(os.path.dirname(output_path) or os.path.dirname(output_path), exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in tqdm(frames, desc="Writing video"):
        out.write(frame)
        
    out.release()
    return output_path

def cleanup_directory(directory: str, extensions: List[str] = None):
    """
    Clean up files in a directory with specific extensions.
    
    Args:
        directory: Directory path to clean
        extensions: List of file extensions to remove (e.g., ['.jpg', '.tmp'])
    """
    if not os.path.exists(directory):
        return
        
    if extensions is None:
        extensions = ['.tmp', '.log']
        
    for filename in os.listdir(directory):
        if any(filename.endswith(ext) for ext in extensions):
            try:
                os.remove(os.path.join(directory, filename))
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def get_video_thumbnail(video_path: str, output_path: str = None, time_sec: float = 1.0) -> Union[str, np.ndarray]:
    """
    Extract a thumbnail from a video at a specific time.
    
    Args:
        video_path: Path to the video file
        output_path: Optional path to save the thumbnail
        time_sec: Time in seconds to extract thumbnail
        
    Returns:
        If output_path provided, returns path to saved image.
        Otherwise returns the thumbnail as numpy array.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_pos = int(fps * time_sec)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"Could not extract thumbnail at {time_sec} seconds")
        
    if output_path:
        os.makedirs(os.path.dirname(output_path) or os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, frame)
        return output_path
        
    return frame