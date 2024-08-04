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
            ["一株利益IFRS", "jpcrp_cor:BasicEarningsLossPerShareIFRSSummaryOfBusinessResults", "CurrentYearDuration", "single"],
            ["一株利益", "jpcrp_cor:BasicEarningsLossPerShareSummaryOfBusinessResults", "CurrentYearDuration", "single"],
        ]

        result: map[str, list] = {}
        for target_items in xbrl_targets:
            name = target_items[0]
            key = target_items[1]
            context_filter = target_items[2]
            is_single = target_items[3] == "single"

            item_list: list[EdinetData] = edinet_xbrl_object.get_data_list(key)

            items = []
            for item in item_list:
                if context_filter in item.get_context_ref():
                    if item.get_value() is None:
                        continue

                    # print(name + ": " + item.get_value() + " " + item.get_context_ref())
                    items.append(item.get_value())
                    if is_single:
                        break

            if len(items) == 0:
                result[name] = "" if is_single else []
            else:
                result[name] = items[0] if is_single else items

        return result

    def __init__(self, xbrl_path):

        parser = EdinetXbrlParser()
        edinet_xbrl_object = parser.parse_file(xbrl_path)
        self._result = self._get_parse_result(edinet_xbrl_object)

    def get_average_board_member_reward(self) -> float:
        number_of_board_members = 0
        total_board_member_reward = 0

        for number in self._result["取締役人数"]:
            number_of_board_members += int(number)

        for reward in self._result["取締役報酬合計"]:
            total_board_member_reward += float(reward)

        if number_of_board_members == 0:
            names = self._result["取締役名"]
            if names is not None:
                number_of_board_members = len(names)
            birthdays = self._result["取締役誕生日"]
            if birthdays is not None:
                number_of_board_members = len(birthdays)

        # dummy
        if number_of_board_members == 0:
            number_of_board_members = 1

        average_board_member_reward = total_board_member_reward / number_of_board_members
        return average_board_member_reward

    def get_average_salary(self) -> float:
        value = self._result["従業員平均年収"]
        if len(value) == 0:
            return 0.0

        return float(value)

    def get_average_board_member_age(self) -> float:
        total_board_member_age = 0
        total_board_member_age_count = 0

        for birthday_str in self._result["取締役誕生日"]:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            total_board_member_age += age
            total_board_member_age_count += 1

        average_board_member_age = float(total_board_member_age) / total_board_member_age_count
        return average_board_member_age

    def get_average_age(self):
        return float(self._result["平均年齢"])

    def get_score_per_stock(self) -> float:
        value_str1 = self._result["流動資産"]
        value_str2 = self._result["有価証券"]
        value_str3 = self._result["負債合計"]
        value_str4 = self._result["発行株式数"]

        if len(value_str1) == 0:
            value1 = 0.0
        else:
            value1 = float(value_str1)

        if len(value_str2) == 0:
            value2 = 0.0
        else:
            value2 = float(value_str2)

        if len(value_str3) == 0:
            value3 = 0.0
        else:
            value3 = float(value_str3)

        if len(value_str4) == 0:
            value4 = 1.0
        else:
            value4 = float(value_str4)

        score_per_stock = (value1 + value2 * 0.6 - value3) / value4
        return score_per_stock

    def get_company_name(self) -> str:
        return self._result["会社名"]

    def get_earnings_loss_per_stock(self) -> float:
        value1 = self._result["一株利益IFRS"]
        value2 = self._result["一株利益"]

        value = 0.0
        if len(value1) != 0:
            value = float(value1)
        if len(value2) != 0:
            value = float(value2)

        return value

    def get_number_of_issued_shares(self) -> int:
        value = self._result["発行株式数"]
        if len(value) == 0:
            return 0

        return int(value)

    def get_number_of_employees(self) -> int:
        value = self._result["従業員数(単体)"]
        if len(value) == 0:
            return 0

        return int(value)
