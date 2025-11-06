from src.video_processor import VideoProcessor
import argparse

def main():
    parser = argparse.ArgumentParser(description="Gemini 1.5 Pro Video Summarization System")
    parser.add_argument('video_path', help="Path to the video file")
    parser.add_argument('--description', help="Optional video description", default="")
    parser.add_argument('--cloud', help="Enable cloud processing", action='store_true')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(use_cloud=args.cloud)
    results = processor.process_video(args.video_path, args.description)
    
    print("\nSummary generated successfully!")
    print(f"Keyframes saved to: {results['keyframes']}")
    print(f"Summary saved to: {results['summary_path']}")
    print("\nSummary Content:")
    print(results['summary'])

if __name__ == "__main__":
    main()