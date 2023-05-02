## download_yt.py

Replace list_of_urls with your own

Install pytube

```bash
pip install pytube
```

In config.yaml set
```yaml
videos_path: <path to save videos>
```

Run downloading script

```bash
python scripts/download_yt.py
```

If you are prompted, authenticate with your google account (this is for not public videos), if you won't be downlaoding not public videos anytime soon, you can change use_oauth to False.




## transcribe.py

get the latest whisper.cpp version -> https://github.com/ggerganov/whisper.cpp/releases

get appropriate model adjust according to your machine, base ones are available here: https://huggingface.co/ggerganov/whisper.cpp/tree/main

but you can probably find language specific versions somewhere


in config.yaml set

```yaml
whisper_cpp_executable_path: <path to your executable>
whisper_models_path: <path to models>
whisper_model_name: <filename of the model>
videos_path: <path to videos you want to transcribe>
audio_path: <where you want to save .wav files>
transcriptions_path: <where you want to save subtitles (.srt)>
```

Setup ffmpeg -> https://ffmpeg.org/download.html, make sure it is on your PATH

Run

```bash
python scripts/transcribe.py
```
