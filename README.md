# list-leetcode
## 简介
输入你的leetcode账号密码，就能立即生成包含题号、标题、链接、难度、总提交数、总通过数、通过率、是否付费和已解决等内容的，所有leetcode题目的CSV文件，或炫酷的Excel文件。

请看下面的截图吧～

![CSV][csv]

![Excel][excel]

[csv]:screenshot/csv.png
[excel]:screenshot/excel.png

## 使用方法
参考example.py，请使用Python 3。

```python
from LeetCode import LeetCode

leetCode = LeetCode()

# 账号密码登录
leetCode.login('user_name', 'password')
# 或者你也可以选择在config.json中保存账号密码，用下面这个方法来登录
# leetCode.login_from_config()

# 获取全部题目详细数据
problem_list = leetCode.get_problem_list()

# 获取中文字典
language_dict = leetCode.get_language_dict('Chinese')
# 或者也可以获取英文字典
# language_dict = leetCode.get_language_dict('English')

# 将全部题目详细数据翻译为指定语言
problem_list = leetCode.to_locale(problem_list, language_dict)

# 保存为Excel文件，需要第三方库openpyxl的支持，使用pip3 install openpyxl安装
leetCode.save_problem_list_as_excel(problem_list, 'out.xlsx', language_dict)
# 或者也可以保存为CSV格式
# leetCode.save_problem_list_as_csv(problem_list, 'out.csv')
```
