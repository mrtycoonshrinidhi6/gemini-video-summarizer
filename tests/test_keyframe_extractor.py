import os
import cv2
import numpy as np
import pytest
from src.keyframe_extractor import KeyframeExtractor
from config.config import Config

@pytest.fixture
def sample_video_path():
    # Create a simple test video (2 seconds, 30fps, with changing content)
    test_video_path = "tests/test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video_path, fourcc, 30.0, (640, 480))
    
    # Frame 0-30: Solid red
    red_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    red_frame[:, :] = (0, 0, 255)  # OpenCV uses BGR
    for _ in range(30):
        out.write(red_frame)
    
    # Frame 31-60: Solid green (significant change)
    green_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    green_frame[:, :] = (0, 255, 0)
    for _ in range(30):
        out.write(green_frame)
    
    out.release()
    yield test_video_path
    os.remove(test_video_path)  # Cleanup after test

@pytest.fixture
def keyframe_extractor():
    return KeyframeExtractor()

def test_extract_frames(keyframe_extractor, sample_video_path):
    frames = keyframe_extractor.extract_frames(sample_video_path)
    assert len(frames) > 0
    assert isinstance(frames[0], np.ndarray)

def test_is_keyframe(keyframe_extractor):
    # Create two test frames
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = frame1.copy()
    
    # Identical frames should not be keyframes
    assert not keyframe_extractor.is_keyframe(frame1, frame2, threshold=0.5)
    
    # Modified frame should be keyframe
    frame2[50:, :] = 255  # Add white rectangle
    assert keyframe_extractor.is_keyframe(frame1, frame2, threshold=0.5)

def test_extract_keyframes(keyframe_extractor, sample_video_path):
    keyframes = keyframe_extractor.extract_keyframes(sample_video_path)
    # Should find at least 2 keyframes (red and green sections)
    assert len(keyframes) >= 2
    # Verify frames are different
    assert not np.array_equal(keyframes[0], keyframes[1])

def test_save_keyframes(keyframe_extractor, sample_video_path, tmp_path):
    keyframes = keyframe_extractor.extract_keyframes(sample_video_path)
    saved_paths = keyframe_extractor.save_keyframes(keyframes, "test_video")
    
    assert len(saved_paths) == len(keyframes)
    for path in saved_paths:
        assert os.path.exists(path)
        assert path.endswith('.jpg')
        # Cleanup
        os.remove(path)