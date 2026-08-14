"""
youtube_uploader.py
-------------------
YouTube Data API v3 integration for automated uploads.
All videos uploaded as PRIVATE (human-in-the-loop publish).

Uses OAuth2 with refresh token (no browser needed after initial setup).

Compliance:
- altered_content: true (2026 AI disclosure)
- Human publishes manually

NO .env dependency - uses config.py
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlencode
from config import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REFRESH_TOKEN,
    YOUTUBE_CHANNEL_ID,
    CHANNELS,
)

DATA_DIR = Path(__file__).parent.parent / "data"
VIDEOS_DIR = DATA_DIR / "videos"


def get_access_token() -> str:
    if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
        raise ValueError(
            "Missing YouTube OAuth credentials. "
            "Check config.py for YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN"
        )
    
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise Exception(f"Failed to get access token: {token_data}")
    
    print(f"[AUTH] Access token obtained successfully")
    return access_token


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    channel: str,
    category_id: str = "28",
    thumbnail_path: Optional[str] = None,
    privacy_status: str = "private",
) -> Dict:
    print(f"\n{'='*60}")
    print(f"YOUTUBE UPLOAD")
    print(f"{'='*60}")
    print(f"Channel: {CHANNELS[channel]['name']}")
    print(f"Title: {title[:60]}...")
    print(f"Privacy: {privacy_status}")
    
    access_token = get_access_token()
    
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:30],
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "alteredContent": True,
        },
    }
    
    upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(os.path.getsize(video_path)),
    }
    
    params = {
        "part": "snippet,status",
        "uploadType": "resumable",
    }
    
    print("\n[UPLOAD] Initializing resumable upload...")
    response = requests.post(
        f"{upload_url}?{urlencode(params)}",
        headers=headers,
        json=body,
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to initialize upload: {response.text}")
    
    upload_session_uri = response.headers.get("Location")
    
    file_size = os.path.getsize(video_path)
    chunk_size = 10 * 1024 * 1024
    
    print(f"[UPLOAD] File size: {file_size / (1024*1024):.1f} MB")
    
    with open(video_path, "rb") as f:
        offset = 0
        while offset < file_size:
            chunk = f.read(chunk_size)
            chunk_end = min(offset + len(chunk), file_size)
            
            headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {offset}-{chunk_end - 1}/{file_size}",
            }
            
            response = requests.put(
                upload_session_uri,
                headers=headers,
                data=chunk,
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get("id")
                print(f"\n[SUCCESS] Video uploaded: https://youtube.com/watch?v={video_id}")
                break
            elif response.status_code == 308:
                progress = int((chunk_end / file_size) * 100)
                print(f"[UPLOAD] Progress: {progress}%")
            else:
                raise Exception(f"Upload failed: {response.text}")
            
            offset = chunk_end
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            upload_thumbnail(video_id, thumbnail_path, access_token)
        except Exception as e:
            print(f"[WARN] Thumbnail upload failed: {e}")
    
    return {
        "video_id": video_id,
        "url": f"https://youtube.com/watch?v={video_id}",
        "status": privacy_status,
    }


def upload_thumbnail(video_id: str, thumbnail_path: str, access_token: str):
    print(f"[THUMBNAIL] Uploading thumbnail...")
    
    url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    
    params = {
        "videoId": video_id,
    }
    
    with open(thumbnail_path, "rb") as f:
        files = {
            "file": ("thumbnail.jpg", f, "image/jpeg"),
        }
        response = requests.post(url, headers=headers, params=params, files=files)
    
    if response.status_code == 200:
        print("[THUMBNAIL] Uploaded successfully")
    else:
        print(f"[WARN] Thumbnail upload response: {response.status_code}")


def batch_upload(videos: list, channel: str, privacy_status: str = "private") -> list:
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
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {success_count}/{len(videos)} uploaded")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("YOUTUBE UPLOADER - TEST MODE")
    print("=" * 60)
    
    try:
        token = get_access_token()
        print(f"[TEST] Access token obtained: {token[:20]}...")
    except Exception as e:
        print(f"[ERROR] Token test failed: {e}")
        print("[HINT] Check YOUTUBE credentials in config.py")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
