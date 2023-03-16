from pypdf import PdfReader

from abc import abstractmethod, ABC
class Lecture(ABC):

    def __init__(self, files):
        self.files = files
        self.lectures = list(self.fetch_lectures())
    
    def fetch_lectures(self):

        for file in self.files:
            yield PdfReader(file)

    @abstractmethod 
    def find_transcriptions(self,reader):
        pass

    def get_transcriptions_from_pdfs(self, path = None):
        '''Get transcriptions from pdfs and save them to a file if path is provided
        
        Transcriptions are saved in a slide by slide format (or time window in future), with each slide separated by a newline.
        Args:
        path (str): path to save the transcriptions to
        Returns:
        list: list of transcriptions
        '''
        transcriptions = []
        for lecture in self.lectures:
            transcriptions.extend(self.find_transcriptions(lecture))
        if path:
            open(path, 'w').write("\n".join(transcriptions))
        return transcriptions

    def get_transcriptions_from_file(self, path):
        '''Get transcriptions from a file,  saved with get_transcriptions_from_pdfs method'''
        return open(path).read().splitlines()
    
    @abstractmethod
    def get_page(self, page_number):
        pass

    def print_pages(self, hits, path):
        from pypdf import PdfWriter

        writer = PdfWriter()
        for hit in hits:
            page = self.get_page(hit["corpus_id"])
            writer.add_page(page)
        writer.write(path)


import re


class DecisionAnalysisLecture(Lecture):

    def __init__(self,files):
        super().__init__(files)

    def find_transcriptions(self,reader):
        PATTERN = re.compile(r'\[[0-9]+\]')
        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            for match in PATTERN.finditer(page_text):
                texts.append(page_text[match.end():])
        return texts
        
    def get_page(self, page_number):
        for i, lecture in enumerate(self.lectures):
            if page_number < len(lecture.pages):
                return lecture.pages[page_number]
            page_number -= len(lecture.pages)
        return None
    




