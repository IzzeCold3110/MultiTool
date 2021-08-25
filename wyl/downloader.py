import threading
import requests
import time
import uuid
import os
import json


class MyDownloader(threading.Thread):
    base_url = None
    running = True
    source_address = None
    target_file = None
    chunk_size = None
    DEFAULT_CHUNK_SIZE = 8192000
    p_chunk_size = None
    p_chunk_size_current = None
    t_name = None
    download_session_uuid = None
    subthreads = []
    debug = False

    report_progress = True
    ready_for_download = False

    def __init__(self, base_url, chunk_size=DEFAULT_CHUNK_SIZE, autostart=True):
        self.base_url = base_url
        if autostart is not True:
            self.running = False
        self.source_address = []
        if chunk_size != self.DEFAULT_CHUNK_SIZE:
            self.chunk_size = chunk_size
        else:
            self.chunk_size = self.DEFAULT_CHUNK_SIZE

        super(MyDownloader, self).__init__()
        self.t_name = self.getName()
        self.download_session_uuid = uuid.uuid4()

    def run(self) -> None:
        json_data_ = {"summary": {}, "data": {}}
        json_data_["summary"]["started_at"] = time.time()

        for dict_item in self.source_address:
            if isinstance(dict_item, dict):
                ready_for_download = False
                head_ = requests.head(self.base_url + dict_item["addr"])
                if head_.status_code == 200:
                    if (self.chunk_size > int(head_.headers["Content-Length"])) is False:
                        ready_for_download = True
                    else:
                        ready_for_download = True

                if ready_for_download is True:
                    self.download(self.base_url + dict_item["addr"], dict_item["target_filepath"])

                if self.debug is True:
                    print(dict_item)

        running = True
        while running is True:
            if self.check_found_alive_subthreads() == 0:
                running = False
            else:
                time.sleep(3)
            time.sleep(0.050)

        if self.debug is True:
            print(len(self.subthreads))
        st_ = []
        for item_ in self.subthreads:
            t_dict = {}
            for k in item_.keys():
                if k != "t":
                    t_dict[k] = item_[k]
            st_.append(t_dict)

        json_data_["data"] = st_
        size_all_ = 0
        for item_ in json_data_["data"]:
            size_all_ += item_["filesize"]["bytes"]
        json_data_["summary"]["size_all"] = {
            "bytes": float("{:.3f}".format(
                int(size_all_))),
            "kBytes": float("{:.3f}".format(
                int(size_all_) / 1024)),
            "MBytes": float("{:.3f}".format(int(size_all_) / 1024 / 1024))
        }

        if self.debug is True:
            for t_ in self.subthreads:
                print("name: " + t_["name"] + " ( " + t_["uuid"] + " )")
                print("start: " + str("{:.4f}".format(t_["started"])))
                print("src: " + t_["source"])
                if "finished" not in t_.keys():
                    print(t_.keys())
                else:
                    print("finished: " + str("{:.4f}".format(t_["finished"])))
                    print("elapsed: " + str("{:.4f}".format(t_["elapsed"])))
                print("")

        for t_ in self.subthreads:
            if t_["t"].is_alive() is False:
                self.subthreads.remove(t_)

        if self.debug is True:
            print(len(self.subthreads))

        json_data_["summary"]["result"] = "Session: " + str(self.download_session_uuid) + " all threads have finished"
        json_data_["summary"]["finished_after_f"] = "{:.4f}".format(time.time() - json_data_["summary"]["started_at"])

        if os.path.isdir(os.path.join(os.getcwd(), DOWNLOAD_FOLDERNAME)):
            with open(os.path.join(os.getcwd(), DOWNLOAD_FOLDERNAME, "status.json"), "w") as json_file:
                json_file.write(json.dumps(json_data_, indent=4))
                json_file.close()

    @staticmethod
    def report_thread_progress(thread_):
        print(thread_.t_name + " | " + thread_.p_report_str)

    def calculate_percent_str(self):
        if self.p_chunk_size_current is not None:
            perc_ = self.p_chunk_size_current / self.p_chunk_size

            if int(perc_ * 100) > 100:
                perc_int = 100
            else:
                perc_int = int(perc_ * 100)

            perc_str_ = str(perc_int) + "%"
            perc_str_t = perc_str_

            expected_len = 5
            while len(perc_str_t) < expected_len:
                perc_str_t += " "
            return perc_str_t + " " + str(self.p_chunk_size_current) + " / " + str(
                self.p_chunk_size)
        else:
            return ""

    def dict_get_key_by_uuid(self, uuid_):
        for i in range(0, len(self.subthreads)):
            if self.subthreads[i]["uuid"] == uuid_:
                return i
        return False

    def get_file(self, source_addr, target_filepath, t_uuid):
        head = requests.head(source_addr)
        self.p_chunk_size = int(head.headers["Content-Length"]) if (
                head.status_code == 200 and "Content-Length" in head.headers.keys()) else 0

        dirname_ = os.path.join(os.getcwd(), DOWNLOAD_FOLDERNAME, os.path.basename(target_filepath).split(".")[1])
        if os.path.isdir(dirname_) is False:
            os.makedirs(dirname_)
        try:
            with open(os.path.join(dirname_, os.path.basename(target_filepath)), "wb") as file_:
                self.p_chunk_size_current = 0
                req = requests.request('GET', source_addr, stream=True)
                subthread_key = self.dict_get_key_by_uuid(t_uuid)
                for data in req.iter_content(self.chunk_size):
                    file_.write(data)

                    self.p_chunk_size_current += self.chunk_size
                self.subthreads[subthread_key]["Content-Type"] = head.headers["Content-Type"]
                self.subthreads[subthread_key]["filesize"] = {
                    "bytes": float("{:.3f}".format(
                        int(head.headers["Content-Length"]))),
                    "kBytes": float("{:.3f}".format(
                        int(head.headers["Content-Length"]) / 1024)),
                    "MBytes": float("{:.3f}".format(int(head.headers["Content-Length"]) / 1024 / 1024))
                }

                self.subthreads[subthread_key]["finished"] = time.time()
                self.subthreads[subthread_key]["elapsed"] = time.time() - self.subthreads[subthread_key]["started"]
                file_.close()
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass
        except IOError:
            pass
        finally:
            file_.close()

    def check_found_alive_subthreads(self):
        found_alive = 0
        for t_ in self.subthreads:
            if t_["t"].is_alive() is True:
                found_alive += 1
        return found_alive

    def add_download(self, download_source_item: dict):
        self.source_address.append(download_source_item)

    def add_downloads(self, download_source: list):
        self.source_address = download_source

    def download(self, target_source, target_filepath) -> None:
        current_uuid = str(uuid.uuid4())
        current_t = threading.Thread(target=self.get_file,
                                     args=(target_source, target_filepath, current_uuid),
                                     daemon=True)
        current_t.start()

        self.subthreads.append({
            "t": current_t,
            "name": self.t_name,
            "source": target_source,
            "target_f": target_filepath,
            "started": float("{:.3f}".format(time.time())),
            "uuid": str(current_uuid),
        })