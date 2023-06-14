import logging
import subprocess
from pathlib import PurePath, Path
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def video_to_wav(path: Path, wav_path: Path) -> int:

    command = f'ffmpeg -i "{path.absolute()}" -ar 16000 -ac 1 -c:a pcm_s16le "{wav_path.absolute()}" -y'
    p = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, err = p.communicate()
    logger.info(f"FFMPEG output: {out}")
    logger.info(f"FFMPEG error: {err}")
    logger.info(f"FFMPEG return code: {p.returncode}")
    return p.returncode


def wav_to_srt(wav_path: Path, srt_path: Path, whisper_executable_path: Path) -> int:
    if srt_path.exists():
        logger.info(f"File {srt_path} already exists, skipping")
        return 0

    command = [
        whisper_executable_path.as_posix(),
        f"{wav_path}",
        "-t",
        "4",  # 4 threads
        "--max-len", # max length in characters
        "16",
        "-l",
        "auto",  # language auto
        "-m", # model
        f"{whisper_model_path.as_posix()}",
        "-osrt",  # output srt
        "-of", # output file
        f"{srt_path.with_suffix('').as_posix()}", # weird choice in whisper.cpp it has to be without extension
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

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_paths", required=True, help="Path to videos or audios (in wav and has to be 16khz)", nargs="+")
    parser.add_argument("--whisper_model_path", required=True, help="Path to whisper model")
    parser.add_argument("--whisper_executable_path", required=True, help="Path to whisper executable")

    args = parser.parse_args()


    whisper_model_path = Path(args.whisper_model_path)
    whisper_executable_path = Path(args.whisper_executable_path)

    for file_path in args.file_paths:

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        if file_path.suffix == ".wav":
            wav_path = file_path
        
        if file_path.suffix == ".mp4":
            wav_path = file_path.with_suffix(".wav")
            srt_path = file_path.with_suffix(".srt")

        if not wav_path.exists():
            video_to_wav(file_path, wav_path)
        else:
            logger.info(f"File {wav_path} already exists, skipping")
        if not srt_path.exists():
            wav_to_srt(wav_path, srt_path, whisper_executable_path)
        else:
            logger.info(f"File {srt_path} already exists, skipping")


