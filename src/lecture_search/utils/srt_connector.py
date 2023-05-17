import logging
from pathlib import Path
from typing import Any, Dict, List

import srt

from lecture_search.utils.file_connector import FileConnector

logger = logging.getLogger(__name__)


class SrtConnector(FileConnector):
    @staticmethod
    def parse_srt_file(srt_file_path: Path) -> List[srt.Subtitle]:
        try:
            with open(srt_file_path, "r") as f:
                srt_file = f.read()
                return list(srt.parse(srt_file))
        except FileNotFoundError:
            logger.error(f"File {srt_file_path} not found")
            return []

    @staticmethod
    def merge_sentences(subtitles: List[srt.Subtitle]) -> List[srt.Subtitle]:
        """Returns a list of subtitles, regrouped by sentences from a srt file"""
        merged_subtitles = []
        current_content = ""
        current_start = None
        current_end = None

        for subtitle in subtitles:
            # merge until we have a full sentence
            current_content += " " + subtitle.content.lstrip().rstrip()
            if current_start is None:
                current_start = subtitle.start
            current_end = subtitle.end
            if current_content[-1] in [
                ".",
                "?",
                "!",
            ]:  # assumption that subtitles end with punctuation
                merged_subtitles.append(
                    srt.Subtitle(
                        index=len(merged_subtitles) + 1,
                        start=current_start,
                        end=current_end,
                        content=current_content.lstrip().rstrip(),
                    )
                )
                current_content = ""
                current_start = None
                current_end = None
        return merged_subtitles

    @staticmethod
    def subtitles_to_json(
        subtitles: List[srt.Subtitle], document_id: str
    ) -> Dict[str, Any]:
        """Converts a list of subtitles to a list of json objects"""
        base_object = {"doc_id": document_id}
        sents = [
            {
                "index": subtitle.index,
                "start": subtitle.start.total_seconds(),
                "end": subtitle.end.total_seconds(),
                "content": subtitle.content,
            }
            for subtitle in subtitles
        ]
        base_object["sents"] = sents
        return base_object

    @staticmethod
    def to_json(file_path: Path) -> Dict[str, Any]:
        subtitles = SrtConnector.parse_srt_file(file_path)
        merged_subtitles = SrtConnector.merge_sentences(subtitles)
        json_object = SrtConnector.subtitles_to_json(merged_subtitles, file_path.stem)
        return json_object

    @staticmethod
    def get_raw_text(file):
        subtitles = SrtConnector.parse_srt_file(file)
        return " ".join([subtitle.content.lstrip().rstrip() for subtitle in subtitles])

    @staticmethod
    def save_srt(file_path: Path, subtitles: List[srt.Subtitle]):
        with open(file_path, "w") as f:
            f.write(srt.compose(subtitles))
