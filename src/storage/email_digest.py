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
        Create an HTML version of the news digest with a complete modern UI revamp
        that is compatible with major email clients and modes.
        
        Args:
            summaries: List of article summary dictionaries
            
        Returns:
            HTML formatted digest
        """
        today = datetime.now().strftime("%B %d, %Y")
        
        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="light dark">
        <title>Tech News Digest</title>
        <style type="text/css">
            /* General reset */
            body {{
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            }}
            table {{
            border-collapse: collapse;
            }}
            /* Container table for center alignment and max-width */
            .container {{
            max-width: 600px;
            width: 100%;
            background-color: #ffffff;
            border: 1px solid #dddddd;
            }}
            /* Header styling */
            .header {{
            background-color: #0A66C2;
            text-align: center;
            padding: 20px;
            color: #ffffff;
            }}
            .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            }}
            .date {{
            font-size: 14px;
            opacity: 0.9;
            }}
            /* Content section */
            .content {{
            padding: 20px;
            color: #333333;
            font-size: 16px;
            line-height: 1.5;
            }}
            /* Article block */
            .article {{
            border-bottom: 1px solid #dddddd;
            padding: 15px 0;
            }}
            .article:last-child {{
            border-bottom: none;
            }}
            .article-title {{
            font-size: 18px;
            color: #0A66C2;
            margin-bottom: 10px;
            font-weight: bold;
            }}
            .meta {{
            margin-bottom: 10px;
            }}
            .source-tag {{
            background-color: #E62117;
            color: #ffffff;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            }}
            .summary {{
            font-size: 14px;
            color: #555555;
            margin: 10px 0;
            }}
            /* Button styling (unchanged as per your note) */
            .article-link {{
            display: inline-block;
            background-color: #7C3AED;
            color: #ffffff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
            border: 1px solid #7C3AED;
            /* Inline !important added if needed in an email client's inline style */
            }}
            .article-link:hover {{
            background-color: #5B21B6;
            border-color: #5B21B6;
            }}
            /* Footer styling */
            .footer {{
            text-align: center;
            font-size: 12px;
            color: #777777;
            padding: 20px;
            border-top: 1px solid #dddddd;
            }}
            .social-links a {{
            color: #0A66C2;
            text-decoration: none;
            margin: 0 5px;
            font-size: 14px;
            }}
        </style>
        </head>
        <body>
        <table width="100%" bgcolor="#f4f4f4" style="padding: 20px 0;">
            <tr>
            <td align="center">
                <table class="container" cellpadding="0" cellspacing="0">
                <!-- Header -->
                <tr>
                    <td class="header" style="background-color: #0A66C2; text-align: center; padding: 20px; color: #ffffff;">
                    <div style="font-size: 32px; margin-bottom: 10px;">📱</div>
                    <h1 style="margin: 0; font-size: 24px; font-weight: bold;">Tech News Digest</h1>
                    <div class="date" style="font-size: 14px; opacity: 0.9;">{today}</div>
                    </td>
                </tr>
                <!-- Content -->
                <tr>
                    <td class="content" style="padding: 20px; color: #333333; font-size: 16px; line-height: 1.5;">
                    <p style="margin: 0 0 20px 0;">Here is your curated digest of today's most important tech stories. Stay informed with the latest news.</p>
        """
        
        # Generate each article block
        article_count = len(summaries)
        for i, summary in enumerate(summaries):
            title = summary.get('title', 'No Title')
            source = summary.get('source', 'Unknown Source')
            link = summary.get('link', 'No link available')
            summary_text = summary.get('summary', '')
            
            html += f"""
                    <div class="article" style="border-bottom: 1px solid #dddddd; padding: 15px 0;">
                        <div class="article-title" style="font-size: 18px; color: #0A66C2; margin-bottom: 10px; font-weight: bold;">{title}</div>
                        <div class="meta" style="margin-bottom: 10px;">
                        <span class="source-tag" style="background-color: #E62117; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-size: 12px;">{source}</span>
                        </div>
                        <div class="summary" style="font-size: 14px; color: #555555; margin: 10px 0;">{summary_text}</div>
                        <a href="{link}" class="article-link" style="display: inline-block; background-color: #7C3AED; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 4px; font-size: 14px; border: 1px solid #7C3AED;">Read Full Article</a>
                    </div>
            """
            
            # Optionally insert a separator block if there are many articles (example after 3 items)
            if i == 2 and article_count > 5:
                html += """
                    <div style="text-align: center; margin: 30px 0; color: #555555; font-size: 14px;">
                        <strong>More trending stories</strong>
                        <div style="border-top: 1px solid #dddddd; margin-top: 10px;"></div>
                    </div>
                """
        
        # Footer section
        html += f"""
                    </td>
                </tr>
                <tr>
                    <td class="footer" style="text-align: center; font-size: 12px; color: #777777; padding: 20px; border-top: 1px solid #dddddd;">
                    <p style="margin: 0 0 10px 0;">Thanks for reading the Tech News Digest for {today}</p>
                    <div class="social-links" style="font-size: 14px;">
                        <a href="https://github.com/VenkatPantham" style="color: #0A66C2; text-decoration: none; margin: 0 5px;">GitHub</a>&bull;
                        <a href="https://www.linkedin.com/in/venkat-pantham/" style="color: #0A66C2; text-decoration: none; margin: 0 5px;">LinkedIn</a>&bull;
                        <a href="https://venkatpantham.github.io/" style="color: #0A66C2; text-decoration: none; margin: 0 5px;">Website</a>
                    </div>
                    </td>
                </tr>
                </table>
            </td>
            </tr>
        </table>
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