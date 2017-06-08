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


if __name__ == '__main__':
    leetCode = LeetCode()
    leetCode.login_from_config()
    leetCode.save_problem_list()
