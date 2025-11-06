import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import os
from tqdm import tqdm
from config.config import Config

class KeyframeExtractor:
    def __init__(self):
        self.config = Config
        self.config.ensure_directories()
        
    def extract_frames(self, video_path):
        """Extract frames from video at specified intervals"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * self.config.FRAME_EXTRACTION_RATE)
        
        frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                frames.append(frame)
            frame_count += 1
            
        cap.release()
        return frames
    
    def is_keyframe(self, frame1, frame2, threshold):
        """Determine if frame is significantly different"""
        if frame1 is None or frame2 is None:
            return True
            
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        score, _ = ssim(gray1, gray2, full=True)
        return score < threshold
    
    def extract_keyframes(self, video_path):
        """Main method to extract keyframes"""
        frames = self.extract_frames(video_path)
        keyframes = []
        prev_frame = None
        
        for frame in tqdm(frames, desc="Processing frames"):
            if self.is_keyframe(prev_frame, frame, self.config.KEYFRAME_THRESHOLD):
                keyframes.append(frame)
            prev_frame = frame
            
        return keyframes
    
    def save_keyframes(self, keyframes, video_name):
        """Save keyframes to output directory"""
        os.makedirs(self.config.KEYFRAMES_DIR, exist_ok=True)
        saved_paths = []
        
        for i, frame in enumerate(keyframes):
            frame_path = os.path.join(
                self.config.KEYFRAMES_DIR,
                f"{video_name}_keyframe_{i}.jpg"
            )
            cv2.imwrite(frame_path, frame)
            saved_paths.append(frame_path)
            
        return saved_paths