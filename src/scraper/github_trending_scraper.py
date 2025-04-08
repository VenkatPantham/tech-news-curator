import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

class GitHubTrendingScraper:
    """
    A class for scraping trending repositories from GitHub.
    
    This class fetches and parses information about trending repositories
    on GitHub, with optional filtering by programming language.
    """
    
    def __init__(self):
        """Initialize the GitHub Trending scraper with base URL and headers."""
        self.base_url = "https://github.com/trending"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        logger.info("Initialized GitHub Trending scraper")
        
    def scrape(self, limit: int = 10, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape trending repositories from GitHub.
        
        Args:
            limit: Maximum number of repositories to scrape
            language: Filter repositories by programming language
            
        Returns:
            List of repository dictionaries
        """
        try:
            url = self.base_url
            if language:
                url += f"?l={language}"
                logger.info(f"Scraping GitHub trending for language: {language}")
            else:
                logger.info("Scraping GitHub trending for all languages")
                
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Error: GitHub returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            repository_boxes = (
                soup.select('article.Box-row') or 
                soup.select('.Box article') or
                soup.select('.Box .Box-row')
            )
            
            if not repository_boxes:
                logger.warning("No repositories found with the current selector. GitHub's HTML structure may have changed.")
                return []
            
            logger.debug(f"Found {len(repository_boxes)} repositories, processing up to {limit}")
            
            for repo in repository_boxes[:limit]:
                try:
                    repo_link_elem = (
                        repo.select_one('h2 a') or 
                        repo.select_one('h1 a') or
                        repo.select_one('a[data-view-component="true"][href*="/"]')
                    )
                    
                    if not repo_link_elem:
                        continue
                        
                    title = repo_link_elem.get_text(strip=True).replace('\n', ' ').strip()
                    title = ' '.join(title.split())
                    
                    link = repo_link_elem['href']
                    if not link.startswith('http'):
                        link = f"https://github.com{link}"
                    
                    description_element = repo.select_one('p') or repo.select_one('.color-fg-muted')
                    description = description_element.get_text(strip=True) if description_element else "No description"
                    
                    stars_element = (
                        repo.select_one('a[href*="stargazers"]') or 
                        repo.select_one('span[aria-label*="star"]') or
                        repo.select_one('a[href*="star"]')
                    )
                    stars = stars_element.get_text(strip=True) if stars_element else "0"
                    
                    # Try to determine the primary language
                    language_element = repo.select_one('span[itemprop="programmingLanguage"]') or repo.select_one('.repo-language-color + span')
                    primary_language = language_element.get_text(strip=True) if language_element else None
                    
                    repos.append({
                        'title': title, 
                        'description': description, 
                        'stars': stars, 
                        'link': link, 
                        'source': 'GitHub Trending',
                        'language': primary_language
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing repository: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(repos)} repositories from GitHub Trending")        
            return repos
            
        except Exception as e:
            logger.error(f"Error scraping GitHub trending: {str(e)}")
            return []
            
    def filter_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Scrape trending repositories for a specific language.
        
        Args:
            language: Programming language to filter by
            
        Returns:
            List of repository dictionaries
        """
        return self.scrape(language=language)