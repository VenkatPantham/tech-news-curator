import requests
import logging
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

class DevToScraper:
    """
    A class for scraping tech articles from Dev.to.
    
    This class handles fetching and parsing article data from Dev.to,
    with robust error handling and rate limiting to avoid being blocked.
    """
    
    def __init__(self):
        """Initialize Dev.to scraper with base URL and request headers."""
        self.base_url = "https://dev.to"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        logger.info("Initialized Dev.to scraper")
        
    def scrape(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape latest articles from Dev.to.
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Scraping top weekly articles from Dev.to (limit: {limit})")
            response = requests.get(f"{self.base_url}/top/week", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Dev.to returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            article_elements = soup.select('div.crayons-story') or soup.select('article.crayons-story') or soup.select('article')
            
            if not article_elements:
                logger.warning("No articles found with the current selector. Dev.to's HTML structure may have changed.")
                return []
                
            logger.info(f"Found {len(article_elements)} articles, processing up to {limit}")
            
            for item in article_elements[:limit]:
                try:
                    title_element = (item.select_one('h2.crayons-story__title') or 
                                    item.select_one('h2') or 
                                    item.select_one('h3'))
                    
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    
                    link_element = (item.select_one('h2.crayons-story__title a') or 
                                   item.select_one('h2 a') or 
                                   item.select_one('a[id^="article-link-"]') or
                                   item.select_one('a'))
                    
                    if not link_element or 'href' not in link_element.attrs:
                        continue
                        
                    link = link_element['href']
                    if not link.startswith('http'):
                        link = self.base_url + link
                        
                    # Try to get the publication date
                    date_element = (item.select_one('time') or 
                                   item.select_one('.crayons-story__meta time') or
                                   item.select_one('.created-at'))
                                   
                    pub_date = None
                    if date_element and date_element.get('datetime'):
                        pub_date = date_element.get('datetime').split('T')[0]
                    else:
                        pub_date = datetime.now().strftime('%Y-%m-%d')
                        
                    # Try to get the author
                    author_element = (item.select_one('.crayons-story__meta a') or 
                                     item.select_one('.profile-preview-card__name'))
                    author = author_element.get_text(strip=True) if author_element else "Unknown"
                    
                    # Try to get tags
                    tags = []
                    tag_elements = item.select('.crayons-tag')
                    for tag in tag_elements:
                        tag_text = tag.get_text(strip=True)
                        if tag_text and tag_text.startswith('#'):
                            tags.append(tag_text[1:])  # Remove the # prefix
                        elif tag_text:
                            tags.append(tag_text)
                    
                    articles.append({
                        'title': title, 
                        'link': link, 
                        'source': 'Dev.to',
                        'date': pub_date,
                        'author': author,
                        'tags': tags
                    })
                    
                    # Add a small delay to avoid being blocked
                    time.sleep(random.uniform(0.2, 0.8))
                    
                except Exception as e:
                    logger.error(f"Error processing Dev.to article: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from Dev.to")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping Dev.to: {str(e)}")
            return []
    
    def parse_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the content of a specific Dev.to article.
        
        Args:
            article: Article dictionary with at least a 'link' key
            
        Returns:
            Article with additional 'content' and 'summary' fields
        """
        try:
            logger.info(f"Parsing article content from: {article['link']}")
            response = requests.get(article['link'], headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Could not fetch article content. Status code: {response.status_code}")
                return {**article, 'content': "Could not fetch content", 'summary': "Could not fetch content"}
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_element = (soup.select_one('div.crayons-article__body') or 
                              soup.select_one('article[data-article-id]') or
                              soup.select_one('div#article-body') or
                              soup.select_one('div.article-content'))
            
            if content_element:
                full_content = content_element.get_text(strip=True)
                # Create a brief summary (first 300 characters)
                summary = full_content[:300] + ("..." if len(full_content) > 300 else "")
            else:
                full_content = "No content found"
                summary = "No content found"
            
            # Get reading time if available
            reading_time_element = soup.select_one('.crayons-article__header__meta__readingtime')
            reading_time = reading_time_element.get_text(strip=True) if reading_time_element else "Unknown read time"
            
            # Return the article with additional data
            return {
                **article,
                'content': full_content,
                'summary': summary,
                'reading_time': reading_time
            }
            
        except Exception as e:
            logger.error(f"Error parsing Dev.to article: {str(e)}")
            return {**article, 'content': "Error fetching content", 'summary': "Error fetching content"}