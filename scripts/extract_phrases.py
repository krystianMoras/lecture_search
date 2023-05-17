import yaml
from pathlib import Path
from lecture_search.utils.keyphraseextractor import KeyPhraseExtractor

config = yaml.safe_load(open("config.yaml"))


if __name__ == "__main__":
    kpe = KeyPhraseExtractor(
        model_path=config["kpe_model_path"], results_path=Path(config["results_path"])
    )
    kpe.extract_from_files(
        [
            r"assets\slides\da-lec1-notes.pdf",
            r"assets\slides\da-lec2-notes.pdf",
            r"assets\slides\da-lec3-notes.pdf",
            r"assets\slides\da-lec4-notes.pdf",
            r"assets\slides\da-lec5-notes.pdf",
            r"assets\slides\da-lec6-notes.pdf",
            r"assets\slides\da-lec7-notes.pdf",
            r"assets\slides\da-lec8-notes.pdf",
            r"assets\slides\da-lec9-notes.pdf",
            r"assets\slides\da-lec10-notes.pdf",
            r"assets\slides\da-lec11-notes.pdf",
            r"assets\slides\da-lec12-notes.pdf",
        ],
        config["candidates_file_name"],
        save_intermediate=config["save_intermediate"],
    )
