import os
import sys
import time
from datetime import datetime


def download_files():
    from wyl.downloader import MyDownloader
    DOWNLOAD_FOLDERNAME = "downloads_9teeth-wyl-online.de_" + datetime.now().strftime("%d%m%Y-%H%M")

    if not os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), DOWNLOAD_FOLDERNAME)):
        os.mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), DOWNLOAD_FOLDERNAME))

    t_start = time.time()
    t = MyDownloader("https://9teeth.wyl-online.de")

    t.add_downloads([
        {
            "addr": "/mp4/Cha Cha Slide (Re-Recorded) (Remastered).mp4",
            "target_filepath": DOWNLOAD_FOLDERNAME + r"/Cha Cha Slide (Re-Recorded) (Remastered).mp4"
        },
        {
            "addr": "/hgt/N55E011.zip",
            "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E011.zip"
        },
        {
            "addr": "/hgt/N55E012.zip",
            "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E012.zip"
        },
        {
            "addr": "/hgt/N55E015.zip",
            "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E015.zip"
        },
        # {
        #   "addr": "/zip/Kling_Die-Kaenguru-Chroniken_9783844907049.zip",
        #   "target_filepath": DOWNLOAD_FOLDERNAME+r"/Kling_Die-Kaenguru-Chroniken_9783844907049.zip"
        # }
    ])

    t.add_download({
        "addr": "/hgt/N55E015.zip",
        "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E015.zip"
    })
    t.add_download({
        "addr": "/hgt/N55E011.zip",
        "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E011.zip"
    })
    t.add_download({
        "addr": "/hgt/N55E012.zip",
        "target_filepath": DOWNLOAD_FOLDERNAME + r"/N55E012.zip"
    })

    t.start()
    while t.is_alive():
        time.sleep(0.005)

    int_elapsed = "{:.4f}".format(time.time() - t_start)
    print("elapsed time: " + str(int_elapsed))
    sys.exit(0)


def glue_pdfs():
    from wyl.pdf import MyPDFReader
    pdf_ = MyPDFReader(fname_filter={"prefix": "TestPDF"}, overwrite_existing=False, debug=True)
    pdf_.start()
    sys.exit(0)


if __name__ == '__main__':
    glue_pdfs()
    # download_files()
