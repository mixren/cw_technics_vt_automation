import tabula as tb  # needs Java 8+ to be installed,  pip install tabula-py
import numpy
import re
from typing import Tuple, List
from seam_model import Seam
from my_pdf_data_model import MyPdfData

class PdfManager:
    def __init__(self, items=()):
        self.l = list(items)

    # Return: left value - sort of exception, right value - the extracted data
    # If all is extracted well left value is None
    def process_pdf(self, pdf_path: str) -> Tuple[str, MyPdfData]:
        data_seam = tb.read_pdf(pdf_path, area = (26, 34, 140, 140), pages = '1')
        if not data_seam:
            return "No seams found", None   
        print(data_seam)

        if not self.__is_correct_data_shape(data_seam[0].values):
            return "Wrong seams table data", None

        no_xray_seams = self.__only_no_xray_seams(data_seam[0].values)
        if not no_xray_seams:
            return "All seams require RT 100%", None  

        spool, n_pages = self.__spool_and_pages_from_pdf(pdf_path)
        print(spool)

        data_seam_type = tb.read_pdf(pdf_path, area = (24, 24, 790, 490), pages = n_pages)
        if not data_seam_type:
            return f"No weld types found. Should be on page {n_pages}.", None  
        seam_types = data_seam_type[0].values[:, 6]  
        print(seam_types)

        if not len(data_seam) == len(data_seam_type):
            return f"Oops. Number of seams on page 1 is different from page {n_pages}.", None  

        return None, MyPdfData(spool, no_xray_seams, seam_types)

    
    # Keep no x-ray seams
    def __only_no_xray_seams(self, seams: numpy.ndarray) -> List[Seam]:
        grouped_seams = []
        # (x, y) e.g. (7, 6), where x is number or rows, y - number of columns. First row: ['AM No.', 'VT', 'PT', 'RT', 'UT', 'MT'], others - Seams.
        for s in seams[1:, :4]:
            seam = Seam(s[0], s[1], s[2], s[3])
            if not seam.with_xray():
                grouped_seams.append(seam)
        return grouped_seams

    '''def __spool_and_pages_from_pdf(self, pdf_path: str) -> Tuple[str, int]:
        import pdfplumber
        spool = ""
        pages = 0
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            pages = len(pdf.pages)
            page_crop_spool = first_page.crop((626, 528, 718, 545), relative = False)
            txt_spool = page_crop_spool.extract_text()  # SPOOL No.\n13-WPP-020-1-03
            spool = re.split(' |\n', txt_spool)[-1]  # 13-WPP-020-1-03
        return spool, pages'''

    def __spool_and_pages_from_pdf(self, pdf_path: str) -> Tuple[str, int]:
        '''Return number of pages and spool as "13-WPP-020-1-03"'''
        import fitz   # pip install pymupdf
        spool = ""
        pages = 0

        with fitz.open(pdf_path) as pdf:
            pages = len(pdf)
            first_page = pdf[0]  # get first page
            rect = fitz.Rect(626, 528, 718, 545)  # define your rectangle here
            text = first_page.get_textbox(rect)  # get text from rectangle
            print(text)

        return spool, pages


    def __is_correct_data_shape(self, seams: numpy.ndarray) -> bool:
        return len(seams.shape) == 2 and seams.shape[0] > 1 and seams.shape[1] >= 4
