import google.generativeai as genai
from config.config import Config
import base64
import os
from tqdm import tqdm

class GeminiIntegration:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
    def encode_image(self, image_path):
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_summary(self, keyframe_paths, video_description=""):
        """Generate video summary using Gemini"""
        prompt = """
        You are an advanced video analysis system. Analyze these keyframes from a video and provide:
        1. A comprehensive summary of the video content
        2. Key moments identified
        3. Main themes and subjects
        4. Any notable visual elements
        5. A timestamp-based breakdown of important sections
        
        Video context: {video_description}
        """.format(video_description=video_description)
        
        # Prepare content with keyframes
        content = [prompt]
        for path in tqdm(keyframe_paths, desc="Processing keyframes"):
            image_data = {
                'mime_type': 'image/jpeg',
                'data': self.encode_image(path)
            }
            content.append(image_data)
            
        # Generate response
        response = self.model.generate_content(content)
        return response.text
    
    def save_summary(self, summary_text, video_name):
        """Save summary to file"""
        os.makedirs(Config.SUMMARIES_DIR, exist_ok=True)
        summary_path = os.path.join(
            Config.SUMMARIES_DIR,
            f"{video_name}_summary.txt"
        )
        
        with open(summary_path, 'w') as f:
            f.write(summary_text)
            
        return summary_path