from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser, EdinetXbrlObject, EdinetData
from datetime import datetime


class XBRLParserWrapper:

    def _get_parse_result(self, edinet_xbrl_object: EdinetXbrlObject):

        xbrl_targets = [
            ["EdinetCode", "jpdei_cor:EDINETCodeDEI", "", "single"],
            ["FilingDate", "jpcrp_cor:FilingDateCoverPage", "", "single"],
            ["会社名", "jpcrp_cor:CompanyNameCoverPage", "", "single"],
            ["会社英名", "jpcrp_cor:CompanyNameInEnglishCoverPage", "", "single"],
            ["本社所在地", "jpcrp_cor:AddressOfRegisteredHeadquarterCoverPage", "", "single"],
            ["社長氏名", "jpcrp_cor:TitleAndNameOfRepresentativeCoverPage", "", "single"],
            ["流動資産", "jppfs_cor:CurrentAssets", "CurrentYearInstant", "single"],
            ["有価証券", "jppfs_cor:InvestmentSecurities", "CurrentYearInstant", "single"],
            ["負債合計", "jppfs_cor:Liabilities", "CurrentYearInstant", "single"],
            ["発行株式数", "jpcrp_cor:TotalNumberOfIssuedSharesSummaryOfBusinessResults", "CurrentYearInstant", "single"],
            ["従業員数(グループ)", "jpcrp_cor:NumberOfEmployees", "CurrentYearInstant", "single"],
            ["従業員数(単体)", "jpcrp_cor:NumberOfEmployees", "CurrentYearInstant_NonConsolidatedMember", "single"],
            ["平均勤続年数", "jpcrp_cor:AverageLengthOfServiceYearsInformationAboutReportingCompanyInformationAboutEmployees", "CurrentYearInstant", "single"],
            ["平均年齢", "jpcrp_cor:AverageAgeYearsInformationAboutReportingCompanyInformationAboutEmployees", "CurrentYearInstant", "single"],
            ["従業員平均年収", "jpcrp_cor:AverageAnnualSalaryInformationAboutReportingCompanyInformationAboutEmployees", "CurrentYearInstant", "single"],
            ["取締役報酬合計", "jpcrp_cor:TotalAmountOfRemunerationEtcRemunerationEtcByCategoryOfDirectorsAndOtherOfficers", "", "multi"],
            ["取締役人数", "jpcrp_cor:NumberOfDirectorsAndOtherOfficersRemunerationEtcByCategoryOfDirectorsAndOtherOfficers", "", "multi"],
            ["取締役名", "jpcrp_cor:NameInformationAboutDirectorsAndCorporateAuditors", "", "multi"],
            ["取締役誕生日", "jpcrp_cor:DateOfBirthInformationAboutDirectorsAndCorporateAuditors", "", "multi"],
        ]

        result: map[str, list]
        for target_items in xbrl_targets:
            name = target_items[0]
            key = target_items[1]
            context_filter = target_items[2]
            is_single = target_items[3] == "single"

            item_list: list[EdinetData] = edinet_xbrl_object.get_data_list(key)

            items = []
            for item in item_list:
                if context_filter in item.get_context_ref():
                    print(name + ": " + item.get_value() + " " + item.get_context_ref())
                    items.append(item.get_value())
                    if is_single:
                        break

            result[name] = items

        return result

    def __init__(self, xbrl_path):

        parser = EdinetXbrlParser()
        edinet_xbrl_object = parser.parse_file(xbrl_path)
        self._result = self._get_parse_result(edinet_xbrl_object)

    def get_average_board_member_reward(self, result) -> int:
        number_of_board_members = 0
        total_board_member_reward = 0

        for number in result["取締役人数"]:
            number_of_board_members += number

        for reward in result["取締役報酬合計"]:
            total_board_member_reward += reward

        average_board_member_reward = total_board_member_reward / number_of_board_members
        return average_board_member_reward

    def get_average_salary(self):
        return self._result["従業員平均年収"]

    def get_average_board_member_age(self, result) -> float:
        total_board_member_age = 0
        total_board_member_age_count = 0

        for birthday_str in result["取締役誕生日"]:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            total_board_member_age += age
            total_board_member_age_count += 1

        average_board_member_age = total_board_member_age / total_board_member_age_count
        return average_board_member_age

    def get_average_age(self):
        return self._result["平均年齢"]

    def get_score_per_stock(self):
        score_per_stock = (self._result["流動資産"] + self._result["有価証券"] * 0.7 - self._result["負債合計"]) / self._result["発行株式数"]
        return score_per_stock

    def get_company_name(self):
        return self._result["会社名"]
