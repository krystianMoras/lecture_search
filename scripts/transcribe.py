import logging
import subprocess
from pathlib import Path
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


videos_path = Path(config["videos_path"])
audio_path = Path(config["audio_path"])
transcriptions_path = Path(config["transcriptions_path"])
whisper_model_path = Path(config["whisper_models_path"]) / config["whisper_model_name"]
whisper_executable_path = Path(config["whisper_cpp_executable_path"])


def get_videos_to_process() -> Path:
    for video in videos_path.iterdir():
        if video.suffix == ".mp4":
            yield video


def video_to_wav(path: Path, wav_path: Path) -> int:
    if wav_path.exists():
        logger.info(f"File {wav_path} already exists, skipping")
        return 0
    command = f'ffmpeg -i "{path.absolute()}" -ar 16000 -ac 1 -c:a pcm_s16le "{wav_path.absolute()}" -y'
    p = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, err = p.communicate()
    logger.info(f"FFMPEG output: {out}")
    logger.info(f"FFMPEG error: {err}")
    logger.info(f"FFMPEG return code: {p.returncode}")
    return p.returncode


def wav_to_srt(wav_path: Path) -> int:
    srt_path = transcriptions_path / wav_path.with_suffix(".wav.srt").name

    if srt_path.exists():
        logger.info(f"File {srt_path} already exists, skipping")
        return 0

    command = [
        whisper_executable_path.as_posix(),
        f"{wav_path}",
        "-t",
        "4",  # 4 threads
        "-l",
        "auto",  # language auto
        "-m",
        f"{whisper_model_path.as_posix()}",
        "-osrt",  # output srt
        "-of",
        f"{srt_path.as_posix()}",
    ]

    logger.info(f"Running command: {command}")
    p2 = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    while p2.poll() is None:
        output = p2.stdout.readline()
        logger.info(output)
    out, err = p2.communicate()

    logger.info(f"Transcription output: {out}")
    logger.info(f"Transcription error: {err}")
    logger.info(f"Transcription return code: {p2.returncode}")
    return p2.returncode


if __name__ == "__main__":
    for video in get_videos_to_process():
        wav_path = audio_path / video.with_suffix(".wav").name
        video_to_wav(video, wav_path)
        wav_to_srt(wav_path)
