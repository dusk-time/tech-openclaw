import os
import urllib.request
import urllib.parse

for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(key, None)

# Search arXiv for geothermal energy papers
query = 'geothermal energy'
encoded_query = urllib.parse.quote(query)
url = 'http://export.arxiv.org/api/query?search_query=all:' + encoded_query + '&max_results=15'

try:
    response = urllib.request.urlopen(url, timeout=20)
    content = response.read().decode('utf-8')
    
    with open('C:\\Users\\28054\\.openclaw\\workspace\\arxiv_results.txt', 'w', encoding='utf-8') as f:
        f.write('=== arXiv Search Results ===\n\n')
        f.write(content)
    print('arXiv results saved')
except Exception as e:
    print('Error: ' + str(e))
