from typing import List, Dict, Any
from pathlib import Path
import logging
from lecture_search.utils.file_connector import FileConnector


logger = logging.getLogger(__name__)


class PdfConnector(FileConnector):
    @staticmethod
    def to_json(file_path: Path) -> Dict[str, Any]:
        raise NotImplementedError
        # regex = r'\[[0-9]+\]'
        # subtitles = SrtConnector.parse_srt_file(file_path)
        # merged_subtitles = SrtConnector.merge_sentences(subtitles)
        # json_object = SrtConnector.subtitles_to_json(merged_subtitles, file_path.stem)
        # return json_object
