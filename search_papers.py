import os
import urllib.request
import urllib.parse
import json

for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(key, None)

query = 'shallow geothermal energy CiteSpace'
encoded_query = urllib.parse.quote(query)
url = 'https://api.semanticscholar.org/graph/v1/paper/search?query=' + encoded_query + '&limit=10&fields=title,authors,year,abstract,citationCount'

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req, timeout=15)
    data = json.loads(response.read().decode('utf-8'))
    
    with open('C:\\Users\\28054\\.openclaw\\workspace\\search_results.txt', 'w', encoding='utf-8') as f:
        f.write('=== Semantic Scholar Search Results ===\n\n')
        for i, paper in enumerate(data.get('data', [])[:10], 1):
            f.write(str(i) + '. Title: ' + paper.get('title') + '\n')
            authors = ', '.join([a.get('name') for a in paper.get('authors', [])[:3]])
            f.write('   Authors: ' + authors + '\n')
            f.write('   Year: ' + str(paper.get('year')) + '\n')
            f.write('   Citations: ' + str(paper.get('citationCount')) + '\n')
            abstract = paper.get('abstract', 'N/A')
            if len(abstract) > 500:
                abstract = abstract[:500] + '...'
            f.write('   Abstract: ' + abstract + '\n\n')
    print('Results saved to search_results.txt')
except Exception as e:
    print('Error: ' + str(e))
