import os
import requests
import io
import zipfile
import pandas as pd
import urllib
from datetime import datetime, timedelta


class EdinetApiWrapper:

    def _generate_date_range_str(self, start_date: datetime, end_date: datetime) -> list[str]:

        current_date = start_date
        date_list = []
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return date_list

    def _save_xbrl_file_from_zip_bytes(self, zip_bytes: bytes, xbrl_path: str) -> bool:

        # extract zip in memory
        with io.BytesIO(zip_bytes) as zb:
            # find .xbrl file
            with zipfile.ZipFile(zb, "r") as zf:
                target_file_name = ""
                for file_name in zf.namelist():
                    # filter out xbrl in PublicDoc dir
                    if "PublicDoc" in file_name and ".xbrl" in file_name:
                        target_file_name = file_name
                        break

                # check if target wasn't be found
                if len(target_file_name) == 0:
                    print("couldn't find xbrl file")
                    return False

                # write out xbrl file
                print(target_file_name)
                with zf.open(target_file_name) as extracted_file:
                    content = extracted_file.read()
                with open(xbrl_path, "w") as xbrl_out:
                    xbrl_out.write(content)
                return True

    def _get_doc_info(self, date_str: str) -> list[tuple[str, str, str]]:

        # get document list on the date
        params = {"date": date_str, "type": 2, "Subscription-Key": self._edinet_api_key}  # 決算書類
        url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
        response = requests.get(url=url, params=params)
        data = response.json()

        # json to DataFrame
        documents = data["results"]
        df = pd.DataFrame(documents)
        df_filtered = df[["docID", "secCode", "edinetCode", "filerName", "docDescription", "submitDateTime"]]

        # フィルタリング
        df_financial = df_filtered[df_filtered["docDescription"].str.contains("有価証券報告書")]

        # まとめ
        result = []
        for index, doc in df_financial.iterrows():
            result.append((doc["edinetCode"], doc["submitDateTime"], doc["docID"]))

        return result

    def _download_zip_and_extract_xbrl(self, doc_id: str, xbrl_path: str) -> bool:

        url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}?type=5&Subscription-Key={self._edinet_api_key}"
        max_loop = 3
        for loop in range(max_loop):
            try:
                with urllib.request.urlopen(url) as res:
                    zip_bytes = res.read()
                break
            except urllib.error.HTTPError as e:
                print("failed to download: " + doc_id + ", " + e.reason)
            except SystemError as e:
                print("something wrong")
            if loop == max_loop - 1:
                print("exceeded retry loop!")
        if zip_bytes is not None:
            return self._save_xbrl_file_from_zip_bytes(zip_bytes, xbrl_path)
        return False

    def __init__(self, edinet_api_key: str, download_path: str):
        self._edinet_api_key = edinet_api_key
        self._download_path = download_path

    def download_xbrl_files(self, start: datetime, end: datetime):
        date_list = self._generate_date_range_str(start, end)

        for date_str in date_list:
            doc_info = self._get_doc_info(date_str)
            for edinet_code, submit_date_time, doc_id in doc_info:
                filename = f"{edinet_code}_{submit_date_time}_{doc_id}.xbrl"
                xbrl_path = os.path.join(self._download_path, filename)

                if os.path.exists(xbrl_path):
                    print("file exists: " + xbrl_path)
                    continue

                self._download_zip_and_extract_xbrl(doc_id, xbrl_path)
