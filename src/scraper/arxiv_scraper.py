import requests
import logging
from xml.etree import ElementTree
from typing import List, Dict, Any
import time
import random

# Configure logger
logger = logging.getLogger(__name__)

class ArxivScraper:
    def __init__(self):
        self.base_url = "https://arxiv.org/api/query"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        logger.info("Initialized arXiv scraper")
        
    def scrape(self, category: str = "cs.AI", limit: int = 10, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape recent papers from arXiv in the specified category.
        
        Args:
            category (str): Category to search, e.g., 'cs.AI' for AI papers
            limit (int): Maximum number of papers to scrape
            fetch_content (bool): Whether to fetch detailed abstracts and metadata
            
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
            
            # Fetch detailed paper information if requested
            if fetch_content:
                papers_with_details = []
                for paper in papers:
                    try:
                        paper_with_details = self.fetch_paper_details(paper)
                        papers_with_details.append(paper_with_details)
                        # Add a small delay between requests
                        time.sleep(random.uniform(0.5, 1.0))
                    except Exception as e:
                        logger.error(f"Error fetching details for paper {paper['title']}: {str(e)}")
                        papers_with_details.append(paper)
                return papers_with_details
            else:
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
                
                # Get the abstract URL
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                paper_id = id_elem.text.strip() if id_elem is not None else None
                
                # Get PDF link if available
                pdf_link = None
                for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href')
                        break
                
                # Extract publication date
                published = entry.find('{http://www.w3.org/2005/Atom}published')
                pub_date = published.text.split('T')[0] if published is not None else None
                
                # Get authors
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name = author.find('{http://www.w3.org/2005/Atom}name')
                    if name is not None and name.text:
                        authors.append(name.text.strip())
                
                # Get categories/tags
                categories = []
                for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
                    term = category.get('term')
                    if term:
                        categories.append(term)
                
                # Create a structured paper dictionary
                paper = {
                    'title': title, 
                    'summary': summary, 
                    'link': paper_id, # arXiv identifier URL
                    'pdf_link': pdf_link,
                    'source': 'arXiv',
                    'date': pub_date,
                    'authors': authors,
                    'categories': categories,
                    'content': summary  # Use summary as initial content
                }
                
                papers.append(paper)
                
            return papers
            
        except Exception as e:
            logger.error(f"Error parsing arXiv response: {e}")
            return []
    
    def fetch_paper_details(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch additional details about a paper from its abstract page.
        
        Args:
            paper: Paper dictionary containing at least an arXiv identifier
            
        Returns:
            Paper dictionary with additional details
        """
        try:
            if not paper.get('link'):
                return paper
            
            # Convert arXiv API URL to abstract page URL
            paper_id = paper['link'].split('/')[-1]
            abstract_url = f"https://arxiv.org/abs/{paper_id}"
            
            logger.debug(f"Fetching additional details from {abstract_url}")
            
            response = requests.get(abstract_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch paper details. Status code: {response.status_code}")
                return paper
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the full abstract/description
            abstract_div = soup.select_one('.abstract') or soup.select_one('#abs-abstract')
            if abstract_div:
                full_abstract = abstract_div.get_text(strip=True)
                # Clean up the abstract (remove "Abstract: " prefix if present)
                if full_abstract.lower().startswith('abstract:'):
                    full_abstract = full_abstract[9:].strip()
                
                paper['content'] = full_abstract
                paper['full_abstract'] = full_abstract
            
            # Get comments if available
            comments_div = soup.select_one('.comments')
            if comments_div:
                paper['comments'] = comments_div.get_text(strip=True)
            
            # Get subjects/categories
            subjects_div = soup.select_one('.subjects')
            if subjects_div:
                paper['subjects'] = subjects_div.get_text(strip=True)
            
            # Get DOI if available
            doi_div = soup.select_one('.doi')
            if doi_div:
                paper['doi'] = doi_div.get_text(strip=True)
            
            return paper
            
        except Exception as e:
            logger.error(f"Error fetching paper details: {str(e)}")
            return paper