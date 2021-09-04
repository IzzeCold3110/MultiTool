import os
import sys
import time
import uuid
import binascii
from datetime import datetime

from wyl.stream import generate_tone
from wyl.queue import run_queue, QueueControl


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


def append_hex(a, b):
    sizeof_b = 0

    # get size of b in bits
    while (len(b) >> sizeof_b) > 0:
        sizeof_b += 1

    # align answer to nearest 4 bits (hex digit)
    sizeof_b += sizeof_b % 4

    return (len(a) << sizeof_b) | len(b)

if __name__ == '__main__':
    # glue_pdfs()
    # download_files()
    # generate_tone()

    q_MainQueueThread = run_queue()
    print(str(time.time())+" mainQueue started")
    time.sleep(1.3)
    q_Control = QueueControl()

    t_last_hex_update = 0
    t_last_hex_update_diff = 0
    last_hex = 0
    while True:
        print(str(time.time()) + " mainQueue addItemEvent")
        uuid_ = uuid.uuid4()
        uuid_bytes = uuid.uuid4().bytes

        hex_val = binascii.hexlify((str(uuid_)+"-"+str(time.time())).encode('utf-8'))
        if last_hex != hex_val:
            print("updated last_hex")
            last_hex = hex_val
            tmp_last_hex_update_diff = float(time.time() - t_last_hex_update)
            print(str(tmp_last_hex_update_diff)+" seconds ago")
            t_last_hex_update = time.time()

        q_Control.append(q_MainQueueThread, {
            "q_itemName": "qItem1_a",
            "q_uuid": str(uuid_),
            "data_Type": "randomData",
            "data_Content": hex_val.decode('utf-8')
        })
        time.sleep(3)
