import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

class EmailDigest:
    """
    Handles the creation and sending of tech news digests via email.
    
    This class manages the formatting of news summaries into both HTML and
    plain text email formats, and handles the SMTP connection for sending
    the digests to recipients.
    """
    
    def __init__(self, 
                 smtp_server: str, 
                 smtp_port: int, 
                 sender_email: str, 
                 sender_password: str):
        """
        Initialize the EmailDigest with SMTP server details.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            sender_email: Email address to send from
            sender_password: Password or app password for the sender email
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
    def create_digest(self, summaries: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Create both plain text and HTML versions of the news digest.
        
        Args:
            summaries: List of article summary dictionaries
            
        Returns:
            Tuple containing (plain_text_digest, html_digest)
        """
        # Create both plain text and HTML versions
        plain_digest = self.create_plain_digest(summaries)
        html_digest = self.create_html_digest(summaries)
        
        return plain_digest, html_digest
    
    def create_plain_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Create a plain text version of the news digest.
        
        Args:
            summaries: List of article summary dictionaries
            
        Returns:
            Plain text formatted digest
        """
        today = datetime.now().strftime("%B %d, %Y")
        digest_content = f"Daily Tech News Digest - {today}\n\n"
        
        for summary in summaries:
            title = summary.get('title', 'No Title')
            source = summary.get('source', 'Unknown Source')
            link = summary.get('link', 'No link available')
            summary_text = summary.get('summary', '')
            
            digest_content += f"**{title}**\n"
            digest_content += f"Source: {source}\n"
            digest_content += f"Link: {link}\n"
            digest_content += f"{summary_text}\n\n"
            digest_content += "---\n\n"
            
        return digest_content
    
    def create_html_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Create an HTML version of the news digest with modern styling.
        
        Args:
            summaries: List of article summary dictionaries
            
        Returns:
            HTML formatted digest
        """
        today = datetime.now().strftime("%B %d, %Y")
        
        # Modern CSS styles for the email
        styles = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            :root {
                --primary-color: #2563EB;
                --primary-light: #DBEAFE;
                --primary-dark: #1E40AF;
                --text-dark: #111827;
                --text-medium: #374151;
                --text-light: #6B7280;
                --bg-light: #F3F4F6;
                --bg-white: #FFFFFF;
                --success: #059669;
                --success-light: #D1FAE5;
                --accent: #7C3AED;
                --accent-light: #EDE9FE;
                --secondary: #EC4899;
                --secondary-light: #FCE7F3;
                --border-color: #E5E7EB;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                --radius: 8px;
            }
            
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: var(--text-dark);
                background-color: var(--bg-light);
                margin: 0;
                padding: 0;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, var(--accent), var(--primary-color));
                color: white;
                border-radius: var(--radius) var(--radius) 0 0;
            }
            
            .header h1 {
                font-weight: 700;
                font-size: 28px;
                margin-bottom: 8px;
                letter-spacing: -0.025em;
            }
            
            .logo {
                font-size: 32px;
                margin-bottom: 10px;
            }
            
            .date {
                font-weight: 400;
                opacity: 0.9;
                font-size: 16px;
            }
            
            .content {
                background-color: var(--bg-white);
                border-radius: 0 0 var(--radius) var(--radius);
                box-shadow: var(--shadow-sm);
                padding: 30px 20px;
                margin-bottom: 20px;
            }
            
            .intro {
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--border-color);
            }
            
            .article {
                background-color: var(--bg-white);
                border-radius: var(--radius);
                box-shadow: var(--shadow-sm);
                padding: 25px;
                margin-bottom: 20px;
                border: 1px solid var(--border-color);
                transition: transform 0.2s ease-in-out;
            }
            
            .article:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow);
            }
            
            .article-title {
                color: var(--primary-color);
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 12px;
                line-height: 1.4;
            }
            
            .meta {
                display: flex;
                align-items: center;
                margin-bottom: 16px;
            }
            
            .source-tag {
                display: inline-block;
                background-color: var(--secondary-light);
                color: var(--secondary);
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }
            
            .summary {
                color: var(--text-medium);
                margin-bottom: 20px;
                font-size: 15px;
                line-height: 1.7;
            }
            
            .article-link {
                display: inline-block;
                background-color: var(--accent);
                color: white;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                transition: background-color 0.2s;
            }
            
            .article-link:hover {
                background-color: var(--primary-dark);
            }
            
            .footer {
                text-align: center;
                padding: 30px 20px;
                color: var(--text-light);
                font-size: 14px;
                border-top: 1px solid var(--border-color);
            }
            
            .social-links {
                margin: 20px 0;
            }
            
            .social-link {
                display: inline-block;
                margin: 0 8px;
                color: var(--accent);
                text-decoration: none;
            }
            
            /* Mobile responsiveness */
            @media only screen and (max-width: 600px) {
                .container {
                    width: 100%;
                    padding: 10px;
                }
                
                .header, .content, .footer {
                    padding: 20px 15px;
                }
                
                .article {
                    padding: 20px;
                }
            }
        </style>
        """
        
        # HTML Email structure
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tech News Digest</title>
            {styles}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">📱</div>
                    <h1>Tech News Digest</h1>
                    <div class="date">{today}</div>
                </div>
                
                <div class="content">
                    <div class="intro">
                        <p>Here's your curated digest of today's most important tech stories. Stay informed with the latest developments in the tech world.</p>
                    </div>
        """
        
        # Add each article
        article_count = len(summaries)
        for i, summary in enumerate(summaries):
            title = summary.get('title', 'No Title')
            source = summary.get('source', 'Unknown Source')
            link = summary.get('link', 'No link available')
            summary_text = summary.get('summary', '')
            
            html += f"""
                    <div class="article">
                        <h2 class="article-title">{title}</h2>
                        <div class="meta">
                            <span class="source-tag">{source}</span>
                        </div>
                        <div class="summary">{summary_text}</div>
                        <a href="{link}" class="article-link">Read Full Article</a>
                    </div>
            """
            
            # Add a "more stories" separator if not the last article
            if i == 2 and article_count > 5:
                html += f"""
                    <div style="text-align: center; margin: 30px 0; color: var(--text-medium);">
                        <p style="font-weight: 500;">More trending stories</p>
                        <div style="border-top: 1px solid var(--border-color); margin-top: 10px;"></div>
                    </div>
                """
        
        # Footer
        html += f"""
                </div>
                
                <div class="footer">
                    <p>Thanks for reading the Tech News Digest for {today}</p>
                    <div class="social-links">
                        <a href="https://github.com/VenkatPantham" class="social-link">GitHub</a> &bull;
                        <a href="https://www.linkedin.com/in/venkat-pantham/" class="social-link">LinkedIn</a> &bull;
                        <a href="https://venkatpantham.github.io/" class="social-link">Website</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def send_digest(self, recipients: List[str], summaries: List[Dict[str, Any]]) -> bool:
        """
        Create and send an email digest to the specified recipients.
        
        Args:
            recipients: List of email addresses to send the digest to
            summaries: List of article summary dictionaries
            
        Returns:
            Boolean indicating success or failure
        """
        if not recipients:
            logger.warning("No recipients provided for email digest")
            return False
            
        if not summaries:
            logger.warning("No summaries provided for email digest")
            return False
            
        try:
            plain_digest, html_digest = self.create_digest(summaries)
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"Daily Tech News Digest - {datetime.now().strftime('%b %d, %Y')}"
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(plain_digest, 'plain')
            part2 = MIMEText(html_digest, 'html')
            
            # The email client will try to render the last part first
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                logger.info(f"Sending email digest to {len(recipients)} recipients")
                server.sendmail(self.sender_email, recipients, msg.as_string())
                
            logger.info("Email digest sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email digest: {str(e)}", exc_info=True)
            return False