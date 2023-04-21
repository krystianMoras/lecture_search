from llama_index.readers.base import BaseReader, Document
from pypdf import PdfReader
import re
import typing
from pathlib import Path
import json
class SlideNotesConnector(BaseReader):
    def load_data(self, slide_notes_paths: typing.List[Path],pattern:str,save_transcriptions_path:Path=None):
        # Connect to your data source and load data
        # Create Document objects from the loaded data
        documents = []
        transcriptions = dict()
        for notes_path in slide_notes_paths:
            if notes_path.suffix == ".pdf":
                reader = PdfReader(notes_path)
                PATTERN = re.compile(pattern)
                for i,page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    doc_id = f"{str(notes_path)}_{i}"

                    for match in PATTERN.finditer(page_text):
                        notes = page_text[match.end():]
                        notes = notes.replace("\ufb01","f").replace("\ufb00","ff").replace("\ufb02","fl").replace("\ufb03","ffi").replace("\ufb04","ffl").replace("\u2019","'").replace("\u2013","-") # todo : move this out of here
                        transcriptions[doc_id] = notes
                        documents.append(Document(text=notes,doc_id=doc_id))
            elif notes_path.suffix == ".json":
                with open(notes_path,"r") as f:
                    transcriptions = json.load(f)
                    for doc_id,notes in transcriptions.items():
                        documents.append(Document(text=notes,doc_id=doc_id))

        if save_transcriptions_path:
            with open(save_transcriptions_path,"w") as f:
                json.dump(transcriptions,f)
        return documents



if __name__ == "__main__":
    da_pattern = r'\[[0-9]+\]'
    print(SlideNotesConnector().load_data([Path("decision_analysis/da-lec1-notes.pdf"),Path("decision_analysis/da-lec2-notes.pdf")],da_pattern,Path(r"C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\nlp\lecture_search\data")/ "transcriptions.json"))