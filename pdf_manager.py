import pdfplumber
import tabula as tb
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
        err_msg = None

        data_seam = tb.read_pdf(pdf_path, area = (26, 34, 140, 140), pages = '1')
        if not data_seam:
            return "No seams found", None   
        print(data_seam)

        # data_seam has header.
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
        if seams.shape[0] > 1:
            for s in seams[1:, :4]:
                seam = Seam(s[0], s[1], s[2], s[3])
                if not seam.with_xray():
                    grouped_seams.append(seam)
        return grouped_seams

    def __spool_and_pages_from_pdf(self, pdf_path: str) -> Tuple[str, int]:
        spool = ""
        pages = 0
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            pages = len(pdf.pages)
            page_crop_spool = first_page.crop((626, 528, 718, 545), relative = False)
            txt_spool = page_crop_spool.extract_text()  # SPOOL No.\n13-WPP-020-1-03
            spool = re.split(' |\n', txt_spool)[-1]  # 13-WPP-020-1-03
        return spool, pages