import yaml
from pathlib import Path
from lecture_search.utils.keyphraseextractor import KeyPhraseExtractor

config = yaml.safe_load(open("config.yaml"))


if __name__ == "__main__":
    kpe = KeyPhraseExtractor(model_path=config["kpe_model_path"],results_path=Path(config["results_path"]))
    kpe.extract_from_files(
        [
            r"assets\transcriptions\Natural language processing - lecture 4 Attention and Transformer.wav.srt.srt",
            r"assets\transcriptions\Natural language processing - lecture 6 Named Entity Recognition (NER).wav.srt.srt",
            r"assets\transcriptions\Natural language processing - lecture 7 GPT.wav.srt.srt",
        ],
        config["candidates_file_name"],
        save_intermediate=config["save_intermediate"],
    )
