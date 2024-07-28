from bs4 import BeautifulSoup
import urllib.parse
import requests
import yfinance as yf


class YahooFinanceJPWrapper:

    def _get_last_path_segment(self, url: str) -> str:
        # URLを解析
        parsed_url = urllib.parse.urlparse(url)

        # パスの最後のスラッシュ以降の部分を取得
        path_segments = parsed_url.path.rstrip("/").split("/")
        return path_segments[-1] if path_segments else ""

    def __init__(self):
        self._company_atag_class = "_1WbkBLD0"
        self._stock_price_class = "_1fofaCjs _2aohzPlv _2eYW5OYe"
        self._aggregate_market_value_class = "_3rXWJKZF _1NrnBlaN"

    def get_company_info(self, company_name: str) -> tuple[int, int, str]:

        # trim
        company_name = company_name.replace("株式会社", "")

        try:
            encoded_company_name = urllib.parse.quote(company_name)
            url = f"https://finance.yahoo.co.jp/search/?query={encoded_company_name}"

            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # find a tag
            a_tags = soup.find_all("a", class_=self._company_atag_class)

            stock_price = -1
            aggregate_market_value = -1
            ticker = ""

            # check in the tag
            for tag in a_tags:
                if not company_name in tag.text:
                    continue

                for span in tag.find_all("span", class_=self._stock_price_class):
                    stock_price = int(span.text.replace(",", ""))

                for span in tag.find_all("span", class_=self._aggregate_market_value_class):
                    aggregate_market_value = int(span.text.replace(",", "")) * 1000000

                ticker = self._get_last_path_segment(tag["href"])

                return (stock_price, aggregate_market_value, ticker)
        except Exception as e:
            print(f"エラーが発生しました: {e}")

        return (-1, -1, "")


class YahooFinanceWrapper:
    def get_stock_price_on_date(ticker: str, date_str: str):
        """
        指定したティッカーと日付に対応する株価を取得する関数

        :param ticker: 株のティッカーシンボル
        :param date: 株価を取得したい日付 (YYYY-MM-DD形式の文字列)
        :return: 指定した日の株価データ (pandas DataFrame)
        """
        # 株価データを取得
        stock = yf.Ticker(ticker)

        # 指定した日付の前後1日分のデータを取得
        data = stock.history(start="2024-02-25", end="2024-03-10")

        # 特定の日の株価データを取得
        if date_str in data.index:
            return data.loc[date_str]
        else:
            return None
