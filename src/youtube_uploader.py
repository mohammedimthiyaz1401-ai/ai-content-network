"""
youtube_uploader.py
-------------------
YouTube Data API v3 integration for automated uploads.
All videos uploaded as PRIVATE (human-in-the-loop publish).

Compliance:
- altered_content: true (2026 AI disclosure)
- Human publishes manually
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
VIDEOS_DIR = DATA_DIR / "videos"
CREDENTIALS_DIR = Path(__file__).parent.parent / "credentials"

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Channel configurations
CHANNEL_CONFIGS = {
    "channel_1": {
        "name": "Aria Future",
        "youtube_channel_id": os.getenv("YOUTUBE_CHANNEL_ID_CH1", ""),
        "category_id": "28",  # Science & Technology
        "default_tags": ["AI", "artificial intelligence", "technology", "future", "passive income"],
    },
    "channel_2": {
        "name": "Future Intelligence News",
        "youtube_channel_id": os.getenv("YOUTUBE_CHANNEL_ID_CH2", ""),
        "category_id": "25",  # News & Politics
        "default_tags": ["AI news", "tech news", "future technology", "breakthrough"],
    },
    "channel_3": {
        "name": "The Mystery Algorithm",
        "youtube_channel_id": os.getenv("YOUTUBE_CHANNEL_ID_CH3", ""),
        "category_id": "24",  # Entertainment
        "default_tags": ["mystery", "internet mystery", "psychology", "reddit"],
    },
}


def get_youtube_service(channel: str):
    """
    Authenticate and get YouTube API service.
    
    Args:
        channel: Channel identifier
    
    Returns:
        YouTube API service object
    """
    creds = None
    token_path = CREDENTIALS_DIR / f"token_{channel}.json"
    client_secret_path = CREDENTIALS_DIR / "client_secret.json"
    
    # Check for existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret_path.exists():
                raise FileNotFoundError(
                    f"Missing {client_secret_path}. "
                    "Download from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    channel: str,
    category_id: str = "28",
    thumbnail_path: Optional[str] = None,
    subtitle_path: Optional[str] = None,
    privacy_status: str = "private",
) -> Dict:
    """
    Upload video to YouTube.
    
    Args:
        video_path: Path to video file
        title: Video title
        description: Video description
        tags: List of tags
        channel: Channel identifier
        category_id: YouTube category ID
        thumbnail_path: Path to thumbnail image
        subtitle_path: Path to .srt subtitle file
        privacy_status: private/public/unlisted
    
    Returns:
        Dict with upload status and video ID
    """
    print(f"\n{'='*60}")
    print(f"YOUTUBE UPLOAD")
    print(f"{'='*60}")
    print(f"Channel: {CHANNEL_CONFIGS[channel]['name']}")
    print(f"Title: {title[:60]}...")
    print(f"Privacy: {privacy_status}")
    
    # Get YouTube service
    youtube = get_youtube_service(channel)
    
    # Prepare upload metadata
    body = {
        "snippet": {
            "title": title[:100],  # YouTube limit
            "description": description,
            "tags": tags[:30],  # YouTube limit
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "alteredContent": True,  # 2026 AI disclosure compliance
        },
    }
    
    # Create media upload object
    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )
    
    # Execute upload
    print("\n[UPLOAD] Starting upload...")
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )
    
    response = None
    
    while response is None:
        status, response = request.next_chunk()
        
        if status:
            progress = int(status.progress() * 100)
            print(f"[UPLOAD] Progress: {progress}%")
    
    video_id = response["id"]
    print(f"\n[SUCCESS] Video uploaded: https://youtube.com/watch?v={video_id}")
    
    # Upload thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            ).execute()
            print(f"[THUMBNAIL] Uploaded successfully")
        except Exception as e:
            print(f"[WARN] Thumbnail upload failed: {e}")
    
    # Upload subtitles (captions)
    if subtitle_path and os.path.exists(subtitle_path):
        try:
            upload_subtitles(youtube, video_id, subtitle_path)
        except Exception as e:
            print(f"[WARN] Subtitle upload failed: {e}")
    
    return {
        "video_id": video_id,
        "url": f"https://youtube.com/watch?v={video_id}",
        "status": privacy_status,
    }


def upload_subtitles(youtube, video_id: str, subtitle_path: str):
    """
    Upload subtitle file to YouTube video.
    
    Args:
        youtube: YouTube API service
        video_id: YouTube video ID
        subtitle_path: Path to .srt file
    """
    print(f"[SUBTITLES] Uploading subtitles...")
    
    body = {
        "snippet": {
            "videoId": video_id,
            "language": "en",
            "name": "English",
            "isDraft": False,
        },
    }
    
    media = MediaFileUpload(
        subtitle_path,
        mimetype="application/x-subrip",
        resumable=True,
    )
    
    youtube.captions().insert(
        part="snippet",
        body=body,
        media_body=media,
    ).execute()
    
    print("[SUBTITLES] Uploaded successfully")


def batch_upload(videos: list, channel: str, privacy_status: str = "private") -> list:
    """
    Upload multiple videos in sequence.
    
    Args:
        videos: List of video metadata dicts
        channel: Channel identifier
        privacy_status: Privacy status for all videos
    
    Returns:
        List of upload results
    """
    results = []
    
    print(f"\n{'='*60}")
    print(f"BATCH UPLOAD - {len(videos)} videos")
    print(f"{'='*60}")
    
    for i, video in enumerate(videos, 1):
        print(f"\n[VIDEO {i}/{len(videos)}]")
        
        try:
            result = upload_video(
                video_path=video["video_path"],
                title=video["title"],
                description=video["description"],
                tags=video.get("tags", []),
                channel=channel,
                thumbnail_path=video.get("thumbnail_path"),
                subtitle_path=video.get("subtitle_path"),
                privacy_status=privacy_status,
            )
            result["success"] = True
            results.append(result)
        
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            results.append({
                "success": False,
                "error": str(e),
                "video_path": video.get("video_path"),
            })
    
    # Summary
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {success_count}/{len(videos)} uploaded")
    print(f"{'='*60}")
    
    return results


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("YOUTUBE UPLOADER - TEST MODE")
    print("=" * 60)
    
    print("\n[TEST] This module requires:")
    print("1. YouTube API credentials in credentials/client_secret.json")
    print("2. YouTube Data API v3 enabled in Google Cloud Console")
    print("3. OAuth consent screen configured")
    
    print("\n[SETUP STEPS]")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create project or select existing")
    print("3. Enable YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials")
    print("5. Download client_secret.json")
    print("6. Place in credentials/client_secret.json")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
