import os
from datetime import datetime
from lib import EdinetApiWrapper
from lib import XBRLParserWrapper
from lib import YahooFinanceJPWrapper

download_path = "downloads"


def download():

    edinet_api_key = ""
    if "EDINET_API_KEY" in os.environ:
        edinet_api_key = os.environ["EDINET_API_KEY"]

    if len(edinet_api_key) == 0:
        print("couldn't find EDINET_API_KEY")
        exit(-1)

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    wrapper = EdinetApiWrapper(edinet_api_key, download_path)

    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 6, 2)
    wrapper.download_xbrl_files(start_date, end_date)


def analyze():

    # ディレクトリ内のxbrlファイル一覧取得

    # ファイル名でソート

    # 同一edinet codeでまとめ

    # 同一単位で解析

    # 現在の株価とscoreを並列に並べる

    pass
