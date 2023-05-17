from lecture_search.utils.file_connector import FileConnector
from pypdf import PdfReader
import re
import typing
from pathlib import Path
import json
from typing import Dict, Any
from nltk import sent_tokenize


class SlideNotesConnector(FileConnector):
    # @staticmethod
    # def read_pdf_file(file_path):
    #     reader = PdfReader(file_path)
    #     da_pattern = re.compile(r'\[[0-9]+\]')

    #     for i,page in enumerate(reader.pages):
    #         page_text = page.extract_text()
    #         for match in da_pattern.finditer(page_text):
    #             notes = page_text[match.end():]
    #             notes = notes.replace("\ufb01","fi").replace("\ufb00","ff").replace("\ufb02","fl").replace("\ufb03","ffi").replace("\ufb04","ffl").replace("\u2019","'").replace("\u2013","-") # todo : move this out of here
    #             transcriptions[doc_id] = notes
    #             documents.append(Document(text=notes,doc_id=doc_id))

    @staticmethod
    def extract_text(file_path, pattern):
        reader = PdfReader(file_path)
        da_pattern = re.compile(pattern)
        total_text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            for match in da_pattern.finditer(page_text):
                notes = page_text[match.end() :]
                notes = (
                    notes.replace("\ufb01", "fi")
                    .replace("\ufb00", "ff")
                    .replace("\ufb02", "fl")
                    .replace("\ufb03", "ffi")
                    .replace("\ufb04", "ffl")
                    .replace("\u2019", "'")
                    .replace("\u2013", "-")
                )  # todo : move this out of here
                total_text.append(notes)
        return "\n".join(total_text)

    @staticmethod
    def save_text(file_path, text):
        with open(file_path, "w") as f:
            f.write(text)

    @staticmethod
    def to_json(file_path: Path) -> Dict[str, Any]:
        text = SlideNotesConnector.extract_text(file_path, r"\[[0-9]+\]")
        paragraphs = text.split("\n")
        sentences = []
        for paragraph in paragraphs:
            sentences += sent_tokenize(paragraph)
        base_object = {"doc_id": file_path.stem}
        sents = [
            {"index": i, "content": sentence} for i, sentence in enumerate(sentences)
        ]
        base_object["sents"] = sents
        return base_object

    @staticmethod
    def get_raw_text(file):
        return SlideNotesConnector.extract_text(file, r"\[[0-9]+\]")


if __name__ == "__main__":
    da_pattern = r"\[[0-9]+\]"
    slides = [
        Path("decision_analysis/da-lec1-notes.pdf"),
        Path("decision_analysis/da-lec2-notes.pdf"),
        Path("decision_analysis/da-lec3-notes.pdf"),
        Path("decision_analysis/da-lec4-notes.pdf"),
        Path("decision_analysis/da-lec5-notes.pdf"),
        Path("decision_analysis/da-lec6-notes.pdf"),
        Path("decision_analysis/da-lec7-notes.pdf"),
        Path("decision_analysis/da-lec8-notes.pdf"),
        Path("decision_analysis/da-lec9-notes.pdf"),
        Path("decision_analysis/da-lec10-notes.pdf"),
        Path("decision_analysis/da-lec11-notes.pdf"),
        Path("decision_analysis/da-lec12-notes.pdf"),
    ]

    for slide in slides:
        text = SlideNotesConnector.extract_text(slide, da_pattern)
        path = Path("assets/text") / (slide.stem + ".txt")
        SlideNotesConnector.save_text(path, text)
