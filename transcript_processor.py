import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import requests

class TranscriptProcessor:
    @staticmethod
    def extract_video_id(url):
        """
        Extracts the video ID from various YouTube URL formats.
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already an 11-char ID
        if len(url) == 11 and re.match(r'[0-9A-Za-z_-]{11}', url):
            return url
            
        return None

    @staticmethod
    def get_transcript(video_id):
        """
        Fetches the transcript for a given video ID.
        """
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=['en'])
            return " ".join([t.text for t in transcript])
        except TranscriptsDisabled:
            raise Exception("Transcripts are disabled for this video.")
        except Exception as e:
            raise Exception(f"Error fetching transcript: {str(e)}")

    @staticmethod
    def get_metadata(video_id):
        """
        Fetches video metadata (title, thumbnail) using oEmbed.
        """
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title"),
                    "thumbnail": data.get("thumbnail_url"),
                    "author": data.get("author_name")
                }
            return {
                "title": f"Video {video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "author": "Unknown"
            }
        except Exception:
            return {
                "title": f"Video {video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "author": "Unknown"
            }
