import os
import urllib.request
import urllib.parse
import json

for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(key, None)

def search_papers(query, filename, max_results=20):
    encoded_query = urllib.parse.quote(query)
    url = 'https://api.semanticscholar.org/graph/v1/paper/search?query=' + encoded_query + '&limit=' + str(max_results) + '&fields=title,authors,year,abstract,citationCount,venue'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('=== ' + query + ' ===\n\n')
            for i, paper in enumerate(data.get('data', [])[:max_results], 1):
                f.write(str(i) + '. Title: ' + paper.get('title') + '\n')
                authors = ', '.join([a.get('name') for a in paper.get('authors', [])[:3]])
                f.write('   Authors: ' + authors + '\n')
                f.write('   Year: ' + str(paper.get('year')) + '\n')
                f.write('   Citations: ' + str(paper.get('citationCount')) + '\n')
                f.write('   Venue: ' + str(paper.get('venue')) + '\n')
                abstract = paper.get('abstract', 'N/A')
                if len(abstract) > 300:
                    abstract = abstract[:300] + '...'
                f.write('   Abstract: ' + abstract + '\n\n')
        print(f'Saved: {filename}')
        return True
    except Exception as e:
        print(f'Error searching {query}: {e}')
        return False

# Search for different topics
search_papers('ground source heat pump energy pile', 'papers_energy_pile.txt', 20)
search_papers('geothermal energy bibliometric analysis', 'papers_bibliometric.txt', 20)
search_papers('shallow geothermal energy CiteSpace', 'papers_citespace.txt', 20)
search_papers('thermal performance energy pile', 'papers_thermal.txt', 20)
search_papers('geothermal energy China international', 'papers_china.txt', 20)
