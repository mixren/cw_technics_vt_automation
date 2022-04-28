from my_pdf_data_model import MyPdfData
from mailmerge import MailMerge # pip install docx-mailmerge
import os

class WordManager:

    PATH_VT_TEMPLATE = 'repo\\VT-Template.docx'

    def __init__(self, items=()):
        self.l = list(items)

    def template_exists(self) -> bool:
        return os.path.exists(self.PATH_VT_TEMPLATE)

    def create_word_from_template(self, path_template: str, path_save_folder: str, pdf_data: MyPdfData, my_drawing: str):
        table_min_len = 11
        ch_unchecked = "□"  # or '\u25A1'
        ch_checked = "x"    # or '\u25A3'

        target_folder_path = os.path.join(path_save_folder, "DWR")
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)
        target_file_path = os.path.join(target_folder_path, f"VT-CWT.{my_drawing}.docx")

        #shutil.copy(path_template, target_path)
        #document = MailMerge(target_path)

        document = MailMerge(path_template)
        # document.get_merge_fields() Check if merge fields exist
        seams_table = [{
            'id': seam.id,
            'dimensions': 'According to the drawing',
            'defects': '-',
            'acceptable': 'X',
            'notacceptable': ""} for seam in pdf_data.seams]
        while len(seams_table) < table_min_len:
            seams_table.append({
            'id': "",
            'dimensions': "",
            'defects': "",
            'acceptable': "",
            'notacceptable': ""})

        my_bw = ch_checked if "BW" in pdf_data.seam_types else ch_unchecked
        my_fw = ch_checked if ("FW" in pdf_data.seam_types) or (any(seam.is_flange_stop() for seam in pdf_data.seams)) else ch_unchecked

        document.merge_rows('id', seams_table)
        document.merge(spool = pdf_data.spool)
        document.merge(drawing_1 = my_drawing)
        document.merge(drawing_2 = my_drawing)
        document.merge(bw = my_bw)
        document.merge(fw = my_fw)
        try:
            document.write(target_file_path)
            print(f"VT successfully generated for {my_drawing}")
        except:
            print(f"Error writing to a '{my_drawing}' Word document. Might be it exists and is opened.")
    