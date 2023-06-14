from pytube import YouTube
from pathlib import Path
from pytube.helpers import safe_filename
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_yt(url, output_path):
    yt = YouTube(url, use_oauth=True)
    vid_path = output_path / (safe_filename(yt.title) + ".mp4")
    if vid_path.exists():
        logger.info(f"Video {yt.title} already downloaded")
        return yt.title
    video = yt.streams.get_lowest_resolution()
    video.download(output_path=output_path)
    logger.info(f"Downloaded {video.default_filename}")
    return video.default_filename


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", required=True, nargs="+", help="List of urls to download")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--output_dir", help="Path to save videos")
    group.add_argument("--output_paths", help="Paths to output videos", nargs="+")

    args = parser.parse_args()

    if args.output_paths:
        assert len(args.urls) == len(args.output_paths), "Number of urls and output paths must be equal"
        for url, output_path in zip(args.urls, args.output_paths):
            # create folders in output path if they don't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            download_yt(url, Path(output_path))
    else:
        for url in args.urls:
            download_yt(url, Path(args.output_path))
