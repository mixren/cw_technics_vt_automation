import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pdf_manager import PdfManager
from word_manager import WordManager
from str_manager import StrManager
from threading import Thread, Lock

#Create an instance of tkinter frame
win= Tk()
#Set the Geometry
win.geometry("750x450")
#Create a Text Box
text= Text(win,width= 80,height=30)
text.pack(pady=20)
#Add a title
win.title('VT Generator')
# Declaring a lock
lock = Lock() ## is needed to lock MailMerge.write(), otherwise race condition.
pdf_manager = PdfManager()
word_manager = WordManager()

def make_drawing_name(path_pdf: text):
    name_pdf = os.path.splitext(os.path.basename(path_pdf))[0]
    if name_pdf.count("-") > 2:
        name_pdf = StrManager.change_last_dash_to_dot(name_pdf)
    return name_pdf + ".00"

#Define a function to clear the text
def clear_text():
   text.delete(1.0, END)

# pdf_path example: C:/Users/SAMS/cw_technics_vt_automation/repo/CWT.MP21-28-162/Rasejumi ceham/MP21-28-162-03.pdf
def generate_vt(pdf_path: str):
    folder_destination = os.path.dirname(os.path.dirname(pdf_path))
    drawing = make_drawing_name(pdf_path) 
    err_msg, my_pdf_data = pdf_manager.process_pdf(pdf_path) 
    if err_msg is not None:
        #text.insert(1.0, f"{drawing} {err_msg} \n") make this shit print from a thread
        print(f"{drawing} {err_msg}")
    else: 
        lock.acquire()
        word_manager.create_word_from_template("repo\VT-Template.docx", folder_destination, my_pdf_data, drawing)
        lock.release()
        #text.insert(1.0, f"{drawing} Word document is successfully generated") 

#Define a function to open the pdf file
def open_pdf():
   files = filedialog.askopenfilenames(title="Select a PDF", filetype=(("PDF Files","*.pdf"),("All Files","*.*")))
   if not word_manager.template_exists():
       text.insert(1.0, f"Word template does not exist. Check \"{word_manager.template_path}\"") 
       return

   #file= filedialog.askopenfilenames(parent=win, title='Select a PDF')
   #if file:
   #for file in files:
   #    generate_vt(file)
   if files:
       clear_text()
       text.insert(1.0, "Begin of the VT generation process \n")
       text.update_idletasks()  
       threads = [Thread(target=generate_vt, args=(file,)) for file in files]    
       for thread in threads:
           thread.start() 
       for thread in threads:
           thread.join()
       text.insert(4.0, "End of the VT generation process")  
       print("End.")

def find_all_rasejumi_file_paths(path_folder: str) -> list:
    file_paths = []
    for root, dirs, files in os.walk(path_folder):
        if StrManager.is_rasejumi_in_string(root.split(os.path.sep)[-1]):
            file_paths.extend([os.path.join(root, f) for f in files])
    return file_paths

# Walk through each nested folder including selected, check if the folder is "rasejumi", generate VTs for each "rasejums"
def open_folder():
    path_folder = filedialog.askdirectory()
    if not word_manager.template_exists():
       text.insert(1.0, f"Template does not exist. Check \"{word_manager.template_path}\"") 
       return
    if path_folder:
        text.insert(1.0, "Begin of the VT generation process \n")
        text.update_idletasks()

        file_paths = find_all_rasejumi_file_paths(path_folder)
        print(file_paths)
        if file_paths:
            response = messagebox.askokcancel("askokcancel", f"{len(file_paths)} files found. Generate VTs?")
            if response == 1:
                threads = [Thread(target=generate_vt, args=(f,)) for f in file_paths]    
                for thread in threads:
                    thread.start() 
                for thread in threads:
                    thread.join()
            else:
                text.insert(3.0, "Cancelled \n")

        else:
            text.insert(3.0, "Can't find \"rasejumi\" folder \n")
        text.insert(4.0, "End of the VT generation process")
        print("End.")
        

#Define function to Quit the window
def quit_app():
   win.destroy()
   
#Create a Menu
my_menu= Menu(win)
win.config(menu=my_menu)
#Add dropdown to the Menus
file_menu=Menu(my_menu,tearoff=False)
my_menu.add_cascade(label="File",menu= file_menu)
file_menu.add_command(label="Select folder",command=open_folder)
file_menu.add_command(label="Select PDF",command=open_pdf)
file_menu.add_command(label="Clear",command=clear_text)
file_menu.add_command(label="Quit",command=quit_app)
win.mainloop()