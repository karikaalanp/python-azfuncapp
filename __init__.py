import logging
import azure.functions as func
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing YouTube transcript request')

    url = req.params.get('url')
    if not url:
        try:
            req_body = req.get_json()
            url = req_body.get('url')
        except ValueError:
            pass

    if not url:
        return func.HttpResponse("Please provide a YouTube video URL", status_code=400)

    video_id = get_video_id(url)
    if not video_id:
        return func.HttpResponse("Invalid YouTube URL", status_code=400)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return func.HttpResponse(transcript_text, mimetype="text/plain", status_code=200)

    except TranscriptsDisabled:
        return func.HttpResponse("Transcripts are disabled for this video", status_code=404)
    except NoTranscriptFound:
        return func.HttpResponse("No transcript found for this video", status_code=404)
    except Exception as e:
        logging.error(f"Error retrieving transcript: {e}")
        return func.HttpResponse(f"Failed to get transcript: {str(e)}", status_code=500)
