import requests
import logging
from xml.etree import ElementTree
from typing import List, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

class ArxivScraper:
    def __init__(self):
        self.base_url = "https://arxiv.org/api/query"
        
    def scrape(self, category: str = "cs.AI", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape recent papers from arXiv in the specified category.
        
        Args:
            category (str): Category to search, e.g., 'cs.AI' for AI papers
            limit (int): Maximum number of papers to scrape
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            query = f"search_query={category}&start=0&max_results={limit}"
            response = requests.get(f"{self.base_url}?{query}", timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Error: arXiv API returned status code {response.status_code}")
                return []
                
            papers = self.parse_response(response.text)
            logger.info(f"Successfully scraped {len(papers)} papers from arXiv ({category})")
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching data from arXiv: {e}")
            return []
            
    def parse_response(self, xml_response: str) -> List[Dict[str, Any]]:
        """
        Parse XML response from arXiv API.
        
        Args:
            xml_response (str): XML response from arXiv API
            
        Returns:
            list: List of paper dictionaries
        """
        try:
            papers = []
            root = ElementTree.fromstring(xml_response)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
                
                # Extract publication date
                published = entry.find('{http://www.w3.org/2005/Atom}published')
                pub_date = published.text.split('T')[0] if published is not None else None
                
                papers.append({
                    'title': title, 
                    'summary': summary, 
                    'link': link, 
                    'source': 'arXiv',
                    'date': pub_date
                })
                
            return papers
            
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            return []