from bs4 import BeautifulSoup
import requests

SRC_URL = 'https://www.besteveralbums.com/'

url = 'https://www.besteveralbums.com/thechart.php'
url += '?src=recognised&ct=All&ctv=All&orderby=DateCreated&sortdir=desc&page=1'
max_page = None

req = requests.get(url)
soup = BeautifulSoup(req.content, "html.parser")
charts = [tag for tag in soup.select('tr')]
charts_data = [tag.select_one('th b a') for tag in soup.select('tr') if tag.select_one('th b a')]

# charts_definition = [
#     tag.select_one('tr td.chartlist[colspan="2"]').get_text(strip=True)
#     for tag in soup.select('tr') 
#     if tag.select_one('tr td.chartlist[colspan="2"]')
# ]
# zipped = dict(zip(charts_data, charts_definition))

# heads = charts[0]


if __name__ == '__main__':

    print('Hello world')
