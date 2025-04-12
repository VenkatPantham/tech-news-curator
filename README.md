# Tech News Curator

Tech News Curator is a tool for aggregating, scraping, and summarizing tech news articles from various sources. It leverages a local summarizer built with [Hugging Face Transformers](https://huggingface.co/transformers/) to provide concise article summaries without incurring API costs.

## Features

- **Multi-source scraping** from popular tech platforms:
  - Hacker News
  - Reddit (configurable subreddits)
  - GitHub Trending repositories
  - ArXiv research papers
  - Dev.to articles
- **Local Summarization:** Summarize articles using a local LLM (default model: `facebook/bart-large-cnn`).
- **Flexible output options**:
  - Markdown files with clean formatting
  - Email digests with modern HTML styling
- **Robust error handling** and comprehensive logging
- **Configurable via environment variables**

## Project Structure

```
tech-news-curator/
├── src/
│   ├── main.py                # Entry point with application orchestration
│   ├── scraper/               # News source scrapers
│   │   ├── hacker_news_scraper.py
│   │   ├── reddit_scraper.py
│   │   ├── github_trending_scraper.py
│   │   ├── arxiv_scraper.py
│   │   ├── devto_scraper.py
│   │   └── __init__.py
│   ├── summarizer/            # Content summarization
│   │   ├── summarizer.py
│   │   └── __init__.py
│   ├── storage/               # Output formatting and delivery
│   │   ├── markdown_storage.py
│   │   ├── email_digest.py
│   │   └── __init__.py
│   └── utils/                 # Utility functions
│       ├── logger.py
│       └── __init__.py
├── logs/                      # Application logs (created at runtime)
├── output/                    # Generated digests (created at runtime)
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
└── .env.example               # Example environment variables
```

## Prerequisites

- Python 3.8+
- [Transformers](https://github.com/huggingface/transformers) library
- [PyTorch](https://pytorch.org/) (or another appropriate backend)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/VenkatPantham/tech-news-curator.git
   cd tech-news-curator
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On macOS or Linux
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

To run the application:

```
python src/main.py
```

### Configuration

The application is configured entirely through environment variables. Set these in your `.env` file or in your system environment:

- `ARTICLES_PER_SOURCE`: Number of articles to fetch per source
- `REDDIT_SUBREDDITS`: Comma-separated list of subreddits to scrape
- `ARXIV_CATEGORIES`: Comma-separated list of arXiv categories
- `OUTPUT_DIRECTORY`: Directory to save markdown digests
- `SEND_EMAIL`: Set to "true" to enable email sending
- `SMTP_EMAIL`: Email address to send digests from
- `SMTP_PASSWORD`: Password or app password for the email account
- `EMAIL_RECIPIENTS`: Comma-separated list of email recipients
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `LOG_FILE`: Name of the log file
- `LOG_DIR`: Directory for log files

### Output

The application generates:

1. A markdown file in the output directory with formatted article summaries
2. An email digest sent to configured recipients (if enabled)
3. Log files with application runtime information

## Extending the Project

### Adding a New Scraper

1. Create a new scraper class in `src/scraper/` following the pattern of existing scrapers
2. Ensure it has a `scrape()` method that returns a list of article dictionaries
3. Add the scraper to `src/scraper/__init__.py`

### Customizing Output Formats

Modify the existing storage classes or create new ones in the `src/storage/` directory.

## License

This project is licensed under the MIT License.
[MIT License](LICENSE)
