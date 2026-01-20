import yt_dlp
import os

def is_playlist(url):
    """
    Check if the URL is a YouTube playlist.
    """
    return 'list=' in url or '/playlist?' in url


def get_download_path():
    """
    Get the download path from user input or use default.
    """
    print("Download Location Options:")
    print("1. Press ENTER to use current directory")
    print("2. Enter a custom folder path")
    print()
    
    custom_path = input("Enter folder path (or press ENTER for default): ").strip()
    
    if not custom_path:
        # Use current directory
        download_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Using default location: {download_path}\n")
        return download_path
    
    # Remove quotes if user copied path with quotes
    custom_path = custom_path.strip('"').strip("'")
    
    # Validate the path
    if os.path.exists(custom_path) and os.path.isdir(custom_path):
        print(f"Using custom location: {custom_path}\n")
        return custom_path
    else:
        print(f"Warning: Path '{custom_path}' doesn't exist or is not a directory.")
        create = input("Would you like to create this folder? (y/n): ").strip().lower()
        
        if create == 'y':
            try:
                os.makedirs(custom_path, exist_ok=True)
                print(f"Created and using: {custom_path}\n")
                return custom_path
            except Exception as e:
                print(f"Error creating folder: {e}")
                print("Falling back to default location.\n")
                return os.path.dirname(os.path.abspath(__file__))
        else:
            print("Falling back to default location.\n")
            return os.path.dirname(os.path.abspath(__file__))


def download_youtube_video(url, download_path=None):
    """
    Download a YouTube video or playlist as MP3 audio in high quality.
    """
    # Get the download path
    if download_path is None:
        download_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check if it's a playlist
    is_playlist_url = is_playlist(url)
    
    # Configure yt-dlp options for MP3 download
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',  # 320kbps quality, falls back to best available
        }],
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [progress_hook],
    }
    
    # Add playlist-specific options if it's a playlist
    if is_playlist_url:
        ydl_opts['noplaylist'] = False  # Download the entire playlist
        print("🎵 Playlist detected! Downloading all videos from the playlist...\n")
    else:
        ydl_opts['noplaylist'] = True  # Only download single video even if URL has playlist parameter
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading from: {url}")
            print(f"Save location: {download_path}\n")
            
            # Get video/playlist info first
            info = ydl.extract_info(url, download=False)
            
            if is_playlist_url and 'entries' in info:
                # It's a playlist
                playlist_title = info.get('title', 'Unknown Playlist')
                video_count = len(list(info['entries']))
                print(f"Playlist: {playlist_title}")
                print(f"Total videos: {video_count}")
                print(f"Uploader: {info.get('uploader', 'Unknown')}\n")
                print("=" * 60)
                
                # Download the playlist
                ydl.download([url])
                print("\n" + "=" * 60)
                print(f"✓ Playlist download completed successfully!")
                print(f"Downloaded {video_count} videos to: {download_path}")
            else:
                # It's a single video
                print(f"Video Title: {info.get('title', 'Unknown')}")
                print(f"Duration: {info.get('duration', 0)} seconds")
                print(f"Uploader: {info.get('uploader', 'Unknown')}\n")
                
                # Download the video
                ydl.download([url])
                print("\n✓ Download completed successfully!")
                print(f"File saved to: {download_path}")
            
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        return False
    
    return True


def progress_hook(d):
    """Display download progress."""
    if d['status'] == 'downloading':
        # Calculate percentage
        if d.get('total_bytes'):
            percent = (d.get('downloaded_bytes', 0) / d['total_bytes']) * 100
            print(f"\rDownloading: {percent:.1f}% | "
                  f"Speed: {d.get('_speed_str', 'N/A')} | "
                  f"ETA: {d.get('_eta_str', 'N/A')}", end='', flush=True)
        else:
            print(f"\rDownloading: {d.get('_percent_str', 'N/A')} | "
                  f"Speed: {d.get('_speed_str', 'N/A')} | "
                  f"ETA: {d.get('_eta_str', 'N/A')}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n\nDownload finished, now converting to MP3...")


def main():
    """Main function to run the downloader."""
    print("=" * 60)
    print("YouTube to MP3 Downloader (High Quality)")
    print("=" * 60)
    print()
    
    # Get download folder from user
    download_folder = get_download_path()
    
    # Array of YouTube URLs to download
    video_urls = [
        "https://youtu.be/v2XRkY27b2s?si=WcJ0JqII1aV0eDVS"
    ]
    
    if not video_urls:
        print("Error: No URLs provided!")
        return
    
    # Process each URL
    total_urls = len(video_urls)
    successful = 0
    failed = 0
    
    print(f"\nTotal videos to download: {total_urls}")
    print("=" * 60)
    
    for index, video_url in enumerate(video_urls, 1):
        print(f"\n{'─' * 60}")
        print(f"Processing [{index}/{total_urls}]")
        print(f"{'─' * 60}")
        
        video_url = video_url.strip()
        
        if not video_url:
            print("Skipping empty URL...")
            failed += 1
            continue
        
        # Validate URL
        if not ('youtube.com' in video_url or 'youtu.be' in video_url):
            print(f"Warning: '{video_url}' doesn't look like a YouTube URL. Skipping...")
            failed += 1
            continue
        
        print()
        result = download_youtube_video(video_url, download_folder)
        
        if result:
            successful += 1
        else:
            failed += 1
        
        print(f"\nProgress: {index}/{total_urls} | ✓ {successful} successful | ✗ {failed} failed")
    
    # Final summary
    print(f"\n{'=' * 60}")
    print("BATCH DOWNLOAD COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total: {total_urls} | ✓ Success: {successful} | ✗ Failed: {failed}")
    print(f"Save location: {download_folder}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
