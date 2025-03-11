import logging
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import azure.functions as func

def get_transcript(videourl):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    # Initialize Selenium with ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        url = f"{videourl}"
        driver.get(url)
        time.sleep(5)  # Give time for the page to load

        # Open transcript (YouTube interface)
        more_button = driver.find_element("xpath", "//button[@aria-label='More actions']")
        more_button.click()
        time.sleep(2)

        transcript_button = driver.find_element("xpath", "//tp-yt-paper-item[@role='option' and contains(text(),'Transcript')]")
        transcript_button.click()
        time.sleep(2)

        # Extract transcript lines
        transcript_lines = driver.find_elements("xpath", "//ytd-transcript-segment-renderer//span[@class='segment-text']")
        transcript = [line.text for line in transcript_lines]

        return transcript

    finally:
        driver.quit()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    video_id = req.params.get('video_id')
    if not video_id:
        return func.HttpResponse(
            "Missing video_id parameter",
            status_code=400
        )

    try:
        transcript = get_transcript(video_id)
        return func.HttpResponse(
            json.dumps(transcript),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Failed to get transcript: {str(e)}")
        return func.HttpResponse(
            f"Failed to get transcript: {str(e)}",
            status_code=500
        )
