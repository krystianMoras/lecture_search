import yaml
from pathlib import Path
from lecture_search.utils.keyphraseextractor import KeyPhraseExtractor
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file_paths", required=True, help="Path to files to extract phrases from (pdf or srt)", nargs="+")
parser.add_argument("--kpe_model_path", required=True, help="Path to kpe model")
parser.add_argument("--results_path", required=True, help="Path to results folder")
parser.add_argument("--candidates_file_name", required=True, help="Name of candidates file")
# boolean flag to save intermediate results
parser.add_argument("--save_intermediate", action='store_true', help="Save intermediate results", default=False)

args = parser.parse_args()
if __name__ == "__main__":
    kpe = KeyPhraseExtractor(
        model_path=args.kpe_model_path, results_path=Path(args.results_path)
    )
    kpe.extract_from_files(
        args.file_paths,
        args.candidates_file_name,
        save_intermediate= args.save_intermediate
    )
