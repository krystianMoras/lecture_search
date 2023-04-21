from llama_index.readers.base import BaseReader, Document
from pypdf import PdfReader
import re
import typing
from pathlib import Path
class SlideNotesConnector(BaseReader):
    def load_data(self, slide_notes_paths: typing.List[Path],pattern:str):
        # Connect to your data source and load data
        # Create Document objects from the loaded data
        documents = []
        for notes_path in slide_notes_paths:
            reader = PdfReader(notes_path)
            PATTERN = re.compile(pattern)
            for i,page in enumerate(reader.pages):
                page_text = page.extract_text()
                doc_id = f"{str(notes_path)}_{i}"

                for match in PATTERN.finditer(page_text):
                    notes = page_text[match.end():]
                    documents.append(Document(text=notes,doc_id=doc_id))
        return documents

if __name__ == "__main__":
    da_pattern = r'\[[0-9]+\]'
    print(SlideNotesConnector().load_data([Path("decision_analysis/da-lec1-notes.pdf")],da_pattern))