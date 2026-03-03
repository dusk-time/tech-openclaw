import os
import urllib.request
import urllib.parse
import json

for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(key, None)

def search_arxiv(query, filename, max_results=15):
    encoded_query = urllib.parse.quote(query)
    url = 'http://export.arxiv.org/api/query?search_query=all:' + encoded_query + '&max_results=' + str(max_results)
    
    try:
        response = urllib.request.urlopen(url, timeout=20)
        content = response.read().decode('utf-8')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('=== arXiv: ' + query + ' ===\n\n')
            f.write(content)
        print(f'Saved: {filename}')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def search_openalex(query, filename, max_results=20):
    encoded_query = urllib.parse.quote(query)
    url = 'https://api.openalex.org/works?search=' + encoded_query + '&per_page=' + str(max_results)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('=== OpenAlex: ' + query + ' ===\n\n')
            for i, paper in enumerate(data.get('results', [])[:max_results], 1):
                f.write(str(i) + '. Title: ' + paper.get('title') + '\n')
                authors = ', '.join([a.get('display_name') for a in paper.get('authorships', [])[:3]])
                f.write('   Authors: ' + authors + '\n')
                f.write('   Year: ' + str(paper.get('publication_year')) + '\n')
                if paper.get('cited_by_count'):
                    f.write('   Citations: ' + str(paper.get('cited_by_count')) + '\n')
                if paper.get('doi'):
                    f.write('   DOI: ' + paper.get('doi') + '\n')
                abstract = paper.get('abstract_inverted_index', '')
                if abstract:
                    f.write('   Abstract: (see DOI)\n')
                f.write('\n')
        print(f'Saved: {filename}')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

# Search OpenAlex (more reliable)
search_openalex('ground source heat pump', 'openalex_gshp.txt', 20)
search_openalex('energy pile geothermal', 'openalex_energy_pile.txt', 20)
search_openalex('geothermal energy China', 'openalex_china.txt', 20)
search_openalex('bibliometric analysis geothermal', 'openalex_bibliometric.txt', 20)
