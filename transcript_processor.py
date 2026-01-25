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
        Fetches the transcript for a given video ID, preferring English but falling back to any available language.
        """
        try:
            # Correct instance-based usage for this version
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            
            try:
                # Try to get English transcript first (manual or generated)
                transcript_data = transcript_list.find_transcript(['en'])
            except:
                # If English not found, get the first available transcript
                # This will catch Hindi, Spanish, etc.
                transcript_data = next(iter(transcript_list))
                
            fetched_transcript = transcript_data.fetch()
            # fetched_transcript is a list of snippet objects (or dicts)
            # Use a safe way to extract text that doesn't evaluate the default branch
            return " ".join([t.text if hasattr(t, 'text') else t['text'] for t in fetched_transcript])
            
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
