## download_yt.py

Replace list_of_urls with your own

Install pytube

```bash
pip install pytube
```

Run downloading script

```bash
python scripts/download_yt.py --urls https://www.youtube.com/watch?v=yL1jKBlE6Es https://www.youtube.com/watch?v=pK7baZjRYEM https://www.youtube.com/watch?v=TBEHIj0l8oA --output_paths "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses\Natural Language Processing\Computational Linguistics" "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses\Natural Language Processing\Prompting of Large Language Models" "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses\Natural Language Processing\Ethics of Large Language Models" 

```

If you are prompted, authenticate with your google account (this is for not public videos), if you won't be downloading not public videos anytime soon, you can change use_oauth to False.


## transcribe.py

get the latest whisper.cpp version -> https://github.com/ggerganov/whisper.cpp/releases

get appropriate model, adjust to your machine, base ones are available here: https://huggingface.co/ggerganov/whisper.cpp/tree/main

but you can probably find language specific versions somewhere

Setup ffmpeg -> https://ffmpeg.org/download.html, make sure it is on your PATH

Run

```bash
python .\scripts\transcribe.py --whisper_executable_path "C:\Program Files\whisper.cpp\main.exe" --whisper_model_path "C:\Users\kryst\Documents\models\whisper\ggml-small-q5_0.bin" --file_paths "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses\Natural Language Processing\Prompting of Large Language Models\Prompting Large Language Models.mp4"
```


## extract_phrases.py

download model from https://huggingface.co/krystianmoras/key_phrase_extraction/blob/main/ucphrase.pt

(Run once if you don't have it already)
```sh
python -m spacy download en_core_web_sm
```

Run phrase extraction
```sh
python .\scripts\extract_phrases.py --file_paths "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses\Natural Language Processing\GPT\Natural language processing - lecture 7 GPT.srt" --kpe_model_path "C:\Users\kryst\Documents\models\ucphrase\ucphrase.pt" --results_path "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\data" --candidates_file_name gpt.json
```

for extraction currently only .srt and pdf files are supported