from pytubefix import YouTube
from pytubefix.cli import on_progress
import os


def download_audio(url, output_path="downloads"):
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Initialize YouTube object with progress callback
        yt = YouTube(url, on_progress_callback=on_progress)

        # Get video title and print it
        print(f"Downloading audio from: {yt.title}")

        # Get the audio-only stream (highest quality)
        audio_stream = yt.streams.get_audio_only()

        # Download the audio
        print("Starting download...")
        audio_file = audio_stream.download(output_path=output_path)

        print(f"Download completed! File saved in: {audio_file}")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


if __name__ == "__main__":
    # Example usage
    # video_url = input("Enter YouTube video URL: ")

    # Example url: Nathan Hulls - Apple Steve Jobs Heres To The Crazy Ones - Nathan Hulls
    video_url = "https://www.youtube.com/watch?v=-z4NS2zdrZc"
    download_audio(video_url)
