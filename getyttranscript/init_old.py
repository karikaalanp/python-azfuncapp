import logging
import json
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    path = req.route_params.get('path')
    params = req.params

    if path == "get_transcript":
        video_id = params.get('video_id')
        if not video_id:
            return func.HttpResponse(
                "Missing video_id parameter",
                status_code=400
            )
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return func.HttpResponse(
                json.dumps(transcript),
                mimetype="application/json",
                status_code=200
            )
        except TranscriptsDisabled:
            return func.HttpResponse(
                "Transcripts are disabled for this video",
                status_code=404
            )
        except Exception as e:
            logging.error(f"Error fetching transcript: {str(e)}")
            return func.HttpResponse(
                f"Error fetching transcript: {str(e)}",
                status_code=500
            )

    elif path == "proxy_request":
        target_url = params.get('url')
        if not target_url:
            return func.HttpResponse(
                "Missing url parameter",
                status_code=400
            )
        try:
            # Forward the request to the target URL
            response = requests.get(target_url)
            return func.HttpResponse(
                response.content,
                mimetype=response.headers.get('Content-Type', 'application/json'),
                status_code=response.status_code
            )
        except Exception as e:
            logging.error(f"Error proxying request: {str(e)}")
            return func.HttpResponse(
                f"Error proxying request: {str(e)}",
                status_code=500
            )

    else:
        return func.HttpResponse(
            "Invalid endpoint",
            status_code=404
        )


""" import logging
import azure.functions as func
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api.proxies import GenericProxyConfig



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
        proxies = {
        'http': 'http://10.10.1.10:3128',
        'https': 'http://10.10.1.10:1080',
        }
        ytt_api = YouTubeTranscriptApi(
            proxy_config=GenericProxyConfig(
                http_url="http://user:pass@my-custom-proxy.org:port",
                https_url="https://user:pass@my-custom-proxy.org:port",
            )
        )
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return func.HttpResponse(transcript_text, mimetype="text/plain", status_code=200)

    except TranscriptsDisabled:
        return func.HttpResponse("Transcripts are disabled for this video", status_code=404)
    except NoTranscriptFound:
        return func.HttpResponse("No transcript found for this video", status_code=404)
    except Exception as e:
        logging.error(f"Error retrieving transcript: {e}")
        return func.HttpResponse(f"Failed to get transcript: {str(e)}", status_code=500)
 """