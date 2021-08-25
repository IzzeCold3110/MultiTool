import sys
import threading
import time
import os

from datetime import datetime
from PyPDF3 import PdfFileMerger, PdfFileReader


class MyPDFReader(threading.Thread):
    is_running = True
    mergedObject = None
    outputFile = None
    pdfFiles_source = None
    b_readyToMerge = False
    filter = None
    overwriteExistingFile = False
    interactive = False
    script_filepath = os.getcwd()
    debug = False
    t_start = None

    def __init__(self, fname_filter: dict = None, overwrite_existing=None, debug=None):
        print(self.script_filepath)

        self.t_start = time.time()
        if debug is not None:
            self.debug = debug
        if overwrite_existing is not None:
            self.overwriteExistingFile = overwrite_existing
        if filter is not None:
            self.filter = fname_filter
            if self.debug is True:
                print(self.filter)
        self.mergedObject = PdfFileMerger()
        self.outputFile = os.path.join(
            os.getcwd(),
            "pdfs",
            "_merged",
            self.filter["prefix"] + "-mergedfilesoutput-" + datetime.now().strftime("%d%m%Y_%H%M%S") + ".pdf"
        )

        super(MyPDFReader, self).__init__()

    @staticmethod
    def stat_to_json(fp: str) -> dict:
        s_obj = os.stat(fp)
        return {k: getattr(s_obj, k) for k in dir(s_obj) if k.startswith('st_')}

    def readable_file_stats(self, file):
        return self.stat_to_json(os.path.join(self.script_filepath, "pdfs", file))

    def append_to_merged(self):
        if self.pdfFiles_source is None:
            self.pdfFiles_source = []
        for file_ in os.listdir(os.path.join(self.script_filepath, "pdfs")):

            #if self.debug is True:
            #    print("all-files: "+file_)

            if self.filter is not None:
                checksDone = 0
                if "prefix" in self.filter:
                    if file_.startswith(self.filter["prefix"]):
                        checksDone += 1
                    if file_.endswith(".pdf"):
                        fileStats_ = self.readable_file_stats(file_)
                        checksDone += 1

                if checksDone == (len(self.filter.keys()) + 1):
                    self.pdfFiles_source.append({"filename": file_, "info": fileStats_})
                    print("pdf_files: "+file_)
            else:
                if file_.endswith(".pdf"):
                    fileStats_ = self.readable_file_stats(file_)
                    self.pdfFiles_source.append({
                        "filename": file_,
                        "info": fileStats_
                    })

        b_readyToMerge = True

        if b_readyToMerge is True:
            for file_f in self.pdfFiles_source:
                self.mergedObject.append(
                    PdfFileReader(os.path.join(self.script_filepath, "pdfs", file_f["filename"]),
                                  'rb'))
            self.merge_pdf()

    def merge_pdf(self):
        if self.debug is True:
            print("out: " + self.outputFile)
        if os.path.isfile(self.outputFile):
            if self.interactive is True:
                print("overwrite?")
                answer = input()
                if answer == "y":
                    print("yes - overwrite")
                    self.mergedObject.write(self.outputFile)
            else:
                if self.overwriteExistingFile:
                    self.mergedObject.write(self.outputFile)
                else:
                    print("Err: file exists: " + os.path.basename(self.outputFile))
                    sys.exit(1)
        else:
            self.mergedObject.write(self.outputFile)

        elapsed_ = "{:.4f}".format(time.time()-self.t_start)
        if self.debug is True:
            print("executed in: "+elapsed_+"ms")

    def run(self) -> None:
        if os.path.isdir(os.path.join(self.script_filepath, "pdfs", "_merged")) is False:
            os.makedirs(os.path.join(self.script_filepath, "pdfs", "_merged"))
        self.append_to_merged()
