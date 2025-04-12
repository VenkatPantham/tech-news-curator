import requests
import logging
import time
import random
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
        
    def scrape(self, limit: int = 10, language: Optional[str] = None, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape trending repositories from GitHub.
        
        Args:
            limit: Maximum number of repositories to scrape
            language: Filter repositories by programming language
            fetch_content: Whether to fetch README and additional repo details
            
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

            # Fetch additional repository details if requested
            if fetch_content:
                logger.info(f"Fetching README and details for {len(repos)} repositories")
                repos_with_content = []
                for repo_data in repos:
                    try:
                        repo_with_content = self.fetch_repository_details(repo_data)
                        repos_with_content.append(repo_with_content)
                        # Add delay to avoid being rate limited
                        time.sleep(random.uniform(0.7, 2.0))
                    except Exception as e:
                        logger.error(f"Error fetching details for {repo_data['title']}: {str(e)}")
                        repos_with_content.append(repo_data)  # Use original repo data
                return repos_with_content
            else:
                return repos
            
        except Exception as e:
            logger.error(f"Error scraping GitHub trending: {str(e)}")
            return []
    
    def fetch_repository_details(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch additional details for a GitHub repository including README content.
        
        Args:
            repo_data: Repository data dictionary with at least a 'link' key
            
        Returns:
            Repository data with additional details and README content
        """
        try:
            repo_url = repo_data['link']
            logger.debug(f"Fetching repository details from: {repo_url}")
            
            # Fetch the main repository page
            response = requests.get(repo_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch repository page. Status code: {response.status_code}")
                return repo_data
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract repository statistics
            stats = {}
            
            # Try to get watch/fork counts
            stat_items = soup.select('a.social-count') or soup.select('.Counter')
            if len(stat_items) >= 2:
                # Usually format is [watch_count, fork_count]
                stats['watchers'] = stat_items[0].get_text(strip=True)
                stats['forks'] = stat_items[1].get_text(strip=True)
            
            # Get README content
            readme_content = ""
            readme_element = soup.select_one('#readme article') or soup.select_one('.Box-body .markdown-body')
            
            if readme_element:
                # Extract text from paragraphs to clean up the content
                paragraphs = readme_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                if paragraphs:
                    readme_content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                    # Create a summary (first 300 characters)
                    readme_summary = readme_content[:500] + ("..." if len(readme_content) > 500 else "")
                else:
                    readme_content = readme_element.get_text(strip=True)
                    readme_summary = readme_content[:500] + ("..." if len(readme_content) > 500 else "")
                
                # Clean up whitespace
                readme_content = ' '.join(readme_content.split())
                readme_summary = ' '.join(readme_summary.split())
            
            # Get last updated timestamp if available
            last_updated = None
            time_element = soup.select_one('relative-time') or soup.select_one('time-ago') or soup.select_one('time')
            if time_element and time_element.get('datetime'):
                last_updated = time_element.get('datetime')
            
            # Return updated repository data
            return {
                **repo_data,
                'stats': stats,
                'readme_content': readme_content,
                'content': readme_content,  # Alias for consistent field naming with other scrapers
                'summary': readme_summary if 'readme_summary' in locals() else repo_data.get('description', ''),
                'last_updated': last_updated
            }
            
        except Exception as e:
            logger.error(f"Error fetching repository details: {str(e)}")
            return repo_data
            
    def filter_by_language(self, language: str, fetch_content: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape trending repositories for a specific language.
        
        Args:
            language: Programming language to filter by
            fetch_content: Whether to fetch README and additional repo details
            
        Returns:
            List of repository dictionaries
        """
        return self.scrape(language=language, fetch_content=fetch_content)