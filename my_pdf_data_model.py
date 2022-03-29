import numpy
from typing import List
from seam_model import Seam

class MyPdfData:
    def __init__(self, spool: str, seams: List[Seam], seam_types: numpy.ndarray):
        self.spool = spool
        self.seams = seams
        self.seam_types = seam_types
