import pytest
from src.video_processor import VideoProcessor
from unittest.mock import Mock, patch

@pytest.fixture
def video_processor():
    return VideoProcessor()

def test_process_video(video_processor, tmp_path):
    # Mock dependencies
    mock_extractor = Mock()
    mock_gemini = Mock()
    
    # Setup mock returns
    mock_extractor.extract_keyframes.return_value = ["frame1", "frame2"]
    mock_extractor.save_keyframes.return_value = ["/path/frame1.jpg", "/path/frame2.jpg"]
    mock_gemini.generate_summary.return_value = "Test summary"
    mock_gemini.save_summary.return_value = "/path/summary.txt"
    
    # Patch the dependencies
    with patch('src.video_processor.KeyframeExtractor', return_value=mock_extractor), \
         patch('src.video_processor.GeminiIntegration', return_value=mock_gemini):
        
        processor = VideoProcessor()
        results = processor.process_video("dummy.mp4", "Test video")
        
        # Verify calls
        mock_extractor.extract_keyframes.assert_called_once_with("dummy.mp4")
        mock_gemini.generate_summary.assert_called_once_with(
            ["/path/frame1.jpg", "/path/frame2.jpg"], 
            "Test video"
        )
        
        # Verify results
        assert results['keyframes'] == ["/path/frame1.jpg", "/path/frame2.jpg"]
        assert results['summary'] == "Test summary"
        assert results['summary_path'] == "/path/summary.txt"

def test_cloud_processing(video_processor):
    # Test cloud processing flag
    with patch('src.video_processor.CloudProcessor') as mock_cloud:
        processor = VideoProcessor(use_cloud=True)
        assert processor.cloud_processor is not None
        mock_cloud.assert_called_once()