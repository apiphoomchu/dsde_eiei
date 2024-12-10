import json
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx


def extract_relevant_info(json_data):
    core_data = json_data.get("abstracts-retrieval-response", {}).get("coredata", {})
    authors = core_data.get("dc:creator", {}).get("author", [])
    keywords = json_data.get("abstracts-retrieval-response", {}).get("authkeywords", {}).get("author-keyword", [])
    doi = core_data.get("prism:doi", "")
    
    return {
        "title": core_data.get("dc:title", ""),
        "abstract": core_data.get("dc:description", ""),
        "publication_name": core_data.get("prism:publicationName", ""),
        "publication_year": core_data.get("prism:coverDate", "").split("-")[0],
        "authors": [author.get("ce:indexed-name", "") for author in authors],
        "keywords": [keyword.get("$", "") for keyword in keywords],
        "doi": doi,
    }

def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            return extract_relevant_info(json_data)
    except Exception as e:
        return {"file": file_path, "error": str(e)}

years = ['2023', '2022', '2021', '2020', '2019', '2018']

# Initialize a list to store all file paths
all_file_paths = []

# Collect all file paths from year-wise folders
for year in years:
    base_dir = os.path.join("data", year)
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            all_file_paths.append(os.path.join(root, file))

# Initialize a list to store processed data
processed_data_all = []

# Loop through all collected file paths and process them
for file_path in all_file_paths:
    result = process_file(file_path)  # Assuming process_file is a defined function
    processed_data_all.append(result)

# Create a DataFrame from the processed data
df = pd.DataFrame(processed_data_all)

# Drop rows with missing 'title' or 'abstract' columns
df.dropna(subset=["title", "abstract"], inplace=True)

# Drop unnecessary columns
df.drop(columns=["error", "file"], inplace=True)

# Initialize an empty DataFrame to accumulate final results
final_df = pd.DataFrame()

# Append the processed data to final_df
final_df = pd.concat([final_df, df], ignore_index=True)

# Save the final DataFrame to a CSV file
final_df.to_csv("data/final_data.csv", index=False)


#Parameters
start = 0
size = 200
total_journals = 2000

articles =[]

## Loop pages
while start < total_journals:
    url = f"https://arxiv.org/search/?query=a&searchtype=all&abstracts=show&order=-announced_date_first&size={size}&start={start}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all(attrs={'class': 'arxiv-result'})

        for result in results:
            # Extract title
            title_elem = result.find(attrs={'class': 'title is-5 mathjax'})
            title = title_elem.get_text(strip=True) if title_elem else None
                
            # Extract keywords
            keyword_elems = result.find_all(attrs={'class': 'tag is-small is-link tooltip is-tooltip-top'})
            keywords = [kw.get('data-tooltip', '').strip() for kw in keyword_elems]
            
            # Extract authors
            author_head = result.find(attrs={'class': 'authors'})
            author_elems = author_head.find_all("a", href=True)
            authors = [author.get_text(strip=True) for author in author_elems]
            
            # Extract abstract
            abstract_elem = result.find(attrs={'class': 'abstract-full has-text-grey-dark mathjax'})
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else None
            
            # Extract date -> using the submitted date (if has a v1 -> use v1 submitted date)
            date_elems = result.find_all(attrs={'class': 'has-text-black-bis has-text-weight-semibold'})
            date = None

            for elem in date_elems:
                if "v1" in elem.get_text(strip=True):
                    date = elem.get_text(strip=True)  
                    break
                if date is None:
                    submitted_elem = result.find(string="Submitted")
                if submitted_elem:
                    date = submitted_elem.find_next(text=True).strip()
                    
            pdf_elem = result.find("a", string="pdf")
            pdf = pdf_elem['href'] if pdf_elem else None
            
            #append data
            articles.append({
                'title': title,
                'keywords': keywords,
                'authors': authors,
                'abstract': abstract,
                'date': date,
                'pdf': pdf
            })
    else:
        print(f"Failed to retrieve data for start={start}. HTTP Status Code: {response.status_code}")
        break
    
    #loop pages (200 journals per time)
    start += size

#Create df
df = pd.DataFrame(articles)
display(df)

csv_path = "arxiv_articles.csv"
df.to_csv(csv_path, index=False)

G = nx.Graph()  # Use Graph() for an undirected graph, or DiGraph() for directed

for index, row in df.iterrows():
    # Extract authors from the article
    authors = row['authors']
    
    # Add authors as nodes and edges connecting them to the article
    for author in authors:
        author_node = f"Author_{author}"
        # Add author node if it doesn't exist
        if not G.has_node(author_node):
            G.add_node(author_node, type="author")

# Save graph to GML
output_gml = "authors_graph.gml"
try:
    nx.write_gml(G, output_gml)
    print(f"Graph saved to {output_gml}")
except Exception as e:
    print(f"Failed to save graph: {e}")

