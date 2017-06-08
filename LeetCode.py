import urllib.request
import urllib.parse
import http.cookiejar
import re
import json
import configparser
import csv


class LeetCode:
    def __init__(self):
        self.base_url = 'https://leetcode.com/'
        cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self.opener.addheaders = [
            ('Host', 'leetcode.com'),
            ('User-Agent',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
            ('Referer', 'https://leetcode.com/accounts/login/')
        ]
        self.problem_list = None

    def login_from_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return self.login(config['DEFAULT']['UserName'], config['DEFAULT']['Password'])

    def login(self, user_name, password):
        with self.opener.open(self.base_url + 'accounts/login/') as f:
            content = f.read().decode('utf-8')
        token = re.findall("name='csrfmiddlewaretoken'\svalue='(.*?)'", content)[0]
        post_data = {
            'csrfmiddlewaretoken': token,
            'login': user_name,
            'password': password
        }
        post_data = urllib.parse.urlencode(post_data)
        with self.opener.open(self.base_url + 'accounts/login/', data=post_data.encode()) as f:
            if f.read().decode().find('Successfully signed in') != -1:
                print('Successfully signed in')
            else:
                print('Failed sign in')

    def get_problem_list(self):
        with self.opener.open(self.base_url + 'api/problems/algorithms/') as f:
            content = f.read().decode('utf-8')
        content = json.loads(content)
        result = []
        for problem in content['stat_status_pairs']:
            result.append({
                'id': problem['stat']['question_id'],
                'title': problem['stat']['question__title'],
                'slug': problem['stat']['question__title_slug'],
                'difficulty': problem['difficulty']['level'],
                'total_submitted': problem['stat']['total_submitted'],
                'total_acs': problem['stat']['total_acs'],
                'acceptance': problem['stat']['total_acs'] / problem['stat']['total_submitted'],
                'paid_only': problem['paid_only'],
                'status': True if problem['status'] else False,
            })
        result.sort(key=lambda x: x['id'])
        return result

    def to_Chinese(self, problems):
        title_chinese = {
            'id': '题号',
            'title': '标题',
            'slug': '链接',
            'difficulty': '难度',
            'total_submitted': '总提交数',
            'total_acs': '总通过数',
            'acceptance': '通过率',
            'paid_only': '付费',
            'status': '已解决'
        }
        problems = [{title_chinese[key]: value for (key, value) in problem.items()} for problem in problems]
        difficulty_chinese = {
            1: '简单',
            2: '中等',
            3: '难'
        }
        bool_chinese = {
            True: '是',
            False: '否'
        }
        for problem in problems:
            problem['难度'] = difficulty_chinese[problem['难度']]
            problem['付费'] = bool_chinese[problem['付费']]
            problem['已解决'] = bool_chinese[problem['已解决']]
        return problems

    def save_problem_list(self, type='csv'):
        if not self.problem_list:
            self.problem_list = self.get_problem_list()
        if type == 'csv':
            with open('leetcode.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.problem_list[0].keys())
                writer.writeheader()
                writer.writerows(self.problem_list)
        elif type == 'excel':
            from openpyxl import Workbook
            from openpyxl.styles import NamedStyle
            from openpyxl.formatting.rule import CellIsRule, DataBarRule
            from openpyxl.styles import PatternFill

            wb = Workbook()
            ws = wb.active
            ws.append(tuple(self.problem_list[0].keys()))
            column_index = {item.value: item.column for item in ws[1]}
            rows = [{column_index[key]: value for (key, value) in problem.items()} for problem in self.problem_list]
            for row in rows:
                ws.append(row)
            style_int = NamedStyle('int')
            style_int.number_format = '0'
            style_str = NamedStyle('str')
            style_str.number_format = '@'
            style_pcnt = NamedStyle('pcnt')
            style_pcnt.number_format = '0.0%'
            for cell in ws[column_index['题号']][1:]:
                cell.style = style_int
            for cell in ws[column_index['总提交数']][1:]:
                cell.style = style_int
            for cell in ws[column_index['总通过数']][1:]:
                cell.style = style_int
            for cell in ws[column_index['标题']][1:]:
                cell.style = style_str
            for cell in ws[column_index['链接']][1:]:
                cell.style = style_str
            for cell in ws[column_index['难度']][1:]:
                cell.style = style_str
            for cell in ws[column_index['付费']][1:]:
                cell.style = style_str
            for cell in ws[column_index['已解决']][1:]:
                cell.style = style_str
            for cell in ws[column_index['通过率']][1:]:
                cell.style = style_pcnt
            red_color = 'ffc7ce'
            green_color = 'c2efcf'
            yellow_color = 'ffeba2'
            red_fill = PatternFill(start_color=red_color, end_color=red_color, fill_type='solid')
            green_fill = PatternFill(start_color=green_color, end_color=green_color, fill_type='solid')
            yellow_fill = PatternFill(start_color=yellow_color, end_color=yellow_color, fill_type='solid')
            ws.conditional_formatting.add(column_index['难度'] + '1:' + column_index['难度'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"简单"'], stopIfTrue=False,
                                                     fill=green_fill))
            ws.conditional_formatting.add(column_index['难度'] + '1:' + column_index['难度'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"中等"'], stopIfTrue=False,
                                                     fill=yellow_fill))
            ws.conditional_formatting.add(column_index['难度'] + '1:' + column_index['难度'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"难"'], stopIfTrue=False,
                                                     fill=red_fill))

            ws.conditional_formatting.add(column_index['付费'] + '1:' + column_index['付费'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"否"'], stopIfTrue=False,
                                                     fill=green_fill))
            ws.conditional_formatting.add(column_index['付费'] + '1:' + column_index['付费'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"是"'], stopIfTrue=False,
                                                     fill=red_fill))

            ws.conditional_formatting.add(column_index['已解决'] + '1:' + column_index['已解决'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"否"'], stopIfTrue=False,
                                                     fill=red_fill))
            ws.conditional_formatting.add(column_index['已解决'] + '1:' + column_index['已解决'] + '1048576',
                                          CellIsRule(operator='equal', formula=['"是"'], stopIfTrue=False,
                                                     fill=green_fill))

            ws.conditional_formatting.add(column_index['通过率'] + '1:' + column_index['通过率'] + '1048576',
                                          DataBarRule(start_type='percentile', start_value=0, end_type='percentile',
                                                      end_value=100, color="FF638EC6", showValue='None'))
            wb.save('data.xlsx')

    def load_data(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            self.problem_list = json.loads(f.read())


if __name__ == '__main__':
    leetCode = LeetCode()
    # leetCode.login_from_config()
    leetCode.load_data('data.json')
    leetCode.problem_list = leetCode.to_Chinese(leetCode.problem_list)
    leetCode.save_problem_list('excel')
