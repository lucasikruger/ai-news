import requests
from bs4 import BeautifulSoup

class ContentProvider:
    def __init__(self):
        pass
    def name(self):
        pass
    def get_content(self):
        pass
    
class PapersWithCodeContentProvider(ContentProvider):
    def __init__(self):
        super().__init__()

    def name(self):
        return "PapersWithCodeContentProvider"
    def get_content(self):
        response = requests.get("https://paperswithcode.com/")
        
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"Error getting content with status code: {response.status_code}")
        

        result = self.get_papers(response)

        return result

    def get_papers(self, response):
        result = []

        soup = BeautifulSoup(response.content, "html.parser")
        for row in soup.select(".infinite-container .row.infinite-item.item.paper-card"):
            paper_dict = self.extract_paper_info(row)

            
            result.append(paper_dict)
        return result

    def extract_paper_info(self, row):
        uid = row.select_one("h1 a")["href"]
        response = requests.get(f"https://paperswithcode.com{uid}")
        

        if response.status_code == 200:
            
        
            soup = BeautifulSoup(response.content, "html.parser")
            paper_abstract_div = soup.select_one(".paper-abstract")
            # Extract the abstract
            abstract = paper_abstract_div.find("p").text.strip()
            # Extract the arXiv URL
            arxiv_url = paper_abstract_div.find("a", class_="badge badge-light")["href"]
        else:
            abstract = ""
            arxiv_url = ""
        
        paper_dict = {
                "title": row.select_one("h1 a").get_text(strip=True),
                "subtitle": row.select_one(".item-strip-abstract").get_text(strip=True),
                "media": row.select_one(".item-image")["style"]
                .split("('")[1]
                .split("')")[0],
                "tags": [
                    a.get_text(strip=True) for a in row.select(".badge-primary a")
                ],
                "stars": int(
                    row.select_one(".entity-stars .badge")
                    .get_text(strip=True)
                    .split(" ")[0]
                    .replace(",", "")
                ),
                "github_link": row.select_one(".item-github-link a")["href"],
                "uid": uid,
                "abstract": abstract,
			    "arxiv_url": arxiv_url
            }
        

        
        return paper_dict
    