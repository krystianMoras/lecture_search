from pytube import YouTube
from pathlib import Path
from pytube.helpers import safe_filename
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


list_of_urls = [
    "https://www.youtube.com/watch?v=DYniFHiqCRE",
    "https://www.youtube.com/watch?v=xHIqmZJejBI",
    "https://www.youtube.com/watch?v=ZJAYyV3e0gU",
]

output_path = Path(config["videos_path"])


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
    for url in list_of_urls:
        download_yt(url, output_path)