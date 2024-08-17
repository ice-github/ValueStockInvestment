from bs4 import BeautifulSoup
import requests


class MinkabuWrapper:
    def __init__(self, company_code: str) -> None:
        url = f"https://minkabu.jp/stock/{company_code}"
        response = requests.get(url)
        self._soup = BeautifulSoup(response.text, "html.parser")
        self._company_code = company_code

    def get_name(self) -> str:
        name = self._soup.find("p", class_="md_stockBoard_stockName")
        return name.text

    def get_target_price(self) -> float:
        target_price = self._soup.find("div", class_="md_target_box_price")
        return float(target_price.text.replace(",", ""))

    def get_research_analysis(self) -> str:
        research_url = f"/stock/{self._company_code}/research"
        research_root = self._soup.find("a", href=research_url)
        if research_root is None:
            return "None"
        research_analysis_prev = research_root.find("p", class_="label")
        research_analysis = research_analysis_prev.find_next_sibling()
        return research_analysis.text

    def get_pick_diag(self) -> str:
        pick_url = f"/stock/{self._company_code}/pick"
        pick_root = self._soup.find("a", href=pick_url)
        if pick_root is None:
            return "None"
        pick_diag_prev = pick_root.find("p", class_="label")
        pick_diag = pick_diag_prev.find_next_sibling()
        return pick_diag.text

    def get_industry_name(self) -> str:
        industry_prev = self._soup.find("span", class_="md_ico_tx theme_link size_s md_head_icon")
        industry = industry_prev.find_next_sibling()
        return industry.text
