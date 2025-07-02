# This is a conceptual script. Actual implementation requires more robust error handling.
# This script would be run inside the 'odysseus_dev' container.
# It combines acquisition, scene detection, and frame extraction.

import os
import subprocess
import psycopg2
import logging
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

# --- Configuration (same as before) ---
DB_NAME = "hockey_analytics"
DB_USER = "hockey_user"
DB_PASS = "strongpassword"
DB_HOST = "odysseus_db"
DB_PORT = "5432"

RAW_VIDEO_DIR = "/workspace/data/raw_video"
CLIPS_DIR = "/workspace/data/processed/clips"
FRAMES_DIR = "/workspace/data/processed/frames"

LOG_FILE = "logs/02_acquire_and_process.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

def download_video(url):
    logging.info(f"Downloading: {url}")
    # Using yt-dlp to download
    # The -o flag specifies the output template
    result = subprocess.run(
        ['yt-dlp', '-f', 'best[ext=mp4]', '-o', f'{RAW_VIDEO_DIR}/%(id)s.%(ext)s', url],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        # Find the downloaded file path from stdout
        for line in result.stdout.splitlines():
            if '[download] Destination:' in line:
                filepath = line.split('Destination: ')[1]
                logging.info(f"Successfully downloaded to {filepath}")
                return filepath
    logging.error(f"Failed to download {url}: {result.stderr}")
    return None

def find_scenes(video_path):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))
    scene_manager.detect_scenes(video, show_progress=True)
    return scene_manager.get_scene_list()

def process_video(video_id, video_path):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Split into clips
    logging.info(f"Splitting {video_path} into clips...")
    scene_list = find_scenes(video_path)
    split_video_ffmpeg(video_path, scene_list, output_dir=CLIPS_DIR)
    for i, scene in enumerate(scene_list):
        start_sec = scene[0].get_seconds()
        end_sec = scene[1].get_seconds()
        clip_path = f"{CLIPS_DIR}/{os.path.basename(video_path).split('.')[0]}-{i+1:03d}.mp4"
        if os.path.exists(clip_path):
            cur.execute(
                "INSERT INTO video_clips (parent_video_id, local_path, start_time_sec, end_time_sec) VALUES (%s, %s, %s, %s)",
                (video_id, clip_path, start_sec, end_sec)
            )
    logging.info(f"Saved {len(scene_list)} clip records to DB.")

    # 2. Extract keyframes (e.g., 2 FPS)
    logging.info(f"Extracting keyframes from {video_path}...")
    video_basename = os.path.basename(video_path).split('.')[0]
    frame_output_folder = os.path.join(FRAMES_DIR, video_basename)
    os.makedirs(frame_output_folder, exist_ok=True)
    frame_output_pattern = os.path.join(frame_output_folder, 'frame-%06d.jpg')
    subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'fps=2', frame_output_pattern])
    # ... logic to find extracted frames and add to DB ...
    
    # 3. Update video status
    cur.execute("UPDATE videos SET processed_status = 'processed' WHERE video_id = %s", (video_id,))
    conn.commit()
    cur.close()
    conn.close()

def main(video_urls):
    conn = get_db_connection()
    cur = conn.cursor()

    for url in video_urls:
        cur.execute("SELECT video_id FROM videos WHERE source_url = %s", (url,))
        if cur.fetchone():
            logging.info(f"URL already processed: {url}")
            continue

        local_path = download_video(url)
        if local_path:
            # Assuming title can be derived from path for simplicity
            title = os.path.basename(local_path)
            cur.execute(
                "INSERT INTO videos (source_url, title, local_path) VALUES (%s, %s, %s) RETURNING video_id",
                (url, title, local_path)
            )
            video_id = cur.fetchone()[0]
            conn.commit()
            logging.info(f"Inserted video {video_id} into DB.")
            process_video(video_id, local_path)

    cur.close()
    conn.close()

if __name__ == '__main__':
    # Ensure the logs directory exists before writing to it
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # --- Video sources to be processed ---
    # Find legal-to-use, Creative Commons, or public domain hockey videos
    SOURCES = [
        "https://www.youtube.com/watch?v=A62011oieL8", # Example: Public Domain Archival Footage
        # Add more YouTube, Archive.org, etc. URLs here
    ]
    main(SOURCES)
