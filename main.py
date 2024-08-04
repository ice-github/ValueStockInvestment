import os
import glob
from datetime import datetime
from lib import EdinetApiWrapper
from lib import XBRLParserWrapper
from lib import YahooFinanceJPWrapper
from lib import MinkabuWrapper

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

    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 7, 31)
    wrapper.download_xbrl_files(start_date, end_date)


def analyze():

    # ディレクトリ内のxbrlファイル一覧取得
    pattern = f"{download_path}/*.xbrl"
    xbrl_paths = sorted(glob.glob(pattern))

    # 同一edinet codeでまとめ
    companies = {}
    for xbrl_path in xbrl_paths:
        edinet_code = xbrl_path.split("_")[0]
        if not edinet_code in companies:
            companies[edinet_code] = []
        companies[edinet_code].append(xbrl_path)

    # 同一単位で解析
    yfjpw = YahooFinanceJPWrapper()
    for edinet_code, xbrl_paths in companies.items():
        for xbrl_path in xbrl_paths:

            wrapper = XBRLParserWrapper(xbrl_path)
            company_name = wrapper.get_company_name()
            if len(company_name) == 0:
                # print("couldn't parse xbrl: " + edinet_code)
                continue

            score_per_stock = wrapper.get_score_per_stock()
            if score_per_stock < 1:
                continue

            earnings_loss_per_stock = wrapper.get_earnings_loss_per_stock()
            if earnings_loss_per_stock < 1:
                continue

            # average_salary = wrapper.get_average_salary()
            # if average_salary < 100 * 10000:
            #     continue

            # number_of_issued_shares = wrapper.get_number_of_issued_shares()
            # number_of_employees = wrapper.get_number_of_employees()
            # earnings_per_employee = earnings_loss_per_stock * number_of_issued_shares / number_of_employees
            # employee_earning_power = earnings_per_employee / average_salary
            # if employee_earning_power < 1.5:
            #     continue

            # average_board_member_reward = wrapper.get_average_board_member_reward()
            # average_board_member_reward_manen = int(average_board_member_reward / 10000)
            # if average_board_member_reward_manen < 1500:
            #     continue

            # employee_average_age = wrapper.get_average_age()

            # print(company_name + ": ", end="")
            # print(str(earnings_loss_per_stock) + ", ", end="")
            # print(str(score_per_stock) + ", ", end="")
            # print(str(employee_earning_power) + ", ", end="")
            # print(str(employee_average_age) + ", ", end="")
            # print(str(average_board_member_reward_manen))
            # continue

            stock_price, aggregate_market_value, ticker = yfjpw.get_company_info(company_name)
            if stock_price < 0:
                continue

            company_code = ticker.split(".")[0]
            if len(company_code) > 4:
                continue

            minkabu = MinkabuWrapper(company_code)
            industry_name = minkabu.get_industry_name()
            if "建設" in industry_name:
                continue

            if "銀行" in industry_name:
                continue

            if "不動産" in industry_name:
                continue

            research_analysis = minkabu.get_research_analysis()
            if "割高" in research_analysis:
                continue
            pick_diag = minkabu.get_pick_diag()
            if "売り" in pick_diag:
                continue

            score_ratio = score_per_stock / stock_price
            if score_ratio < 0.1:
                continue

            per = stock_price / earnings_loss_per_stock
            if per > 10:
                continue

            critical_ratio = score_ratio / per

            print(company_name + ": ", end="")
            print(str(score_ratio) + " / ", end="")
            print(str(per) + " = ", end="")
            print(str(critical_ratio) + ", ", end="")
            print(str(stock_price) + ", ", end="")
            print(industry_name + ", ", end="")
            print(research_analysis + ", ", end="")
            print(pick_diag)


# download()
analyze()
