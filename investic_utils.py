from datetime import datetime, timedelta
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key for accessing the GPT model
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)

# Function to convert processed data into structured rows
def convert_to_rows(data):
    """
    Converts nested data structure into a list of dictionaries with
    keys: 'Date', 'stock', 'sentiment', 'topic'.

    Args:
        data (list): Nested data containing stock analysis results.

    Returns:
        list: A flat list of dictionaries for easy processing.
    """
    rows = []
    for entry in data:
        for date, stocks in entry.items():
            for stock, details in stocks.items():
                rows.append({
                    "Date": date,
                    "stock": stock,
                    "sentiment": details["sentiment"],
                    "topic": ", ".join(details["topics"])
                })
    return rows

# Function to extract and decode Bangkok Post news article URL
def extract_BangkokPost_news(url):
    """
    Extracts and decodes the Bangkok Post article URL.

    Args:
        url (str): Encoded URL containing the article link.

    Returns:
        str: Decoded full article URL.
    """
    href_start = url.find("href=") + 5
    href_end = url.find("&", href_start)
    encoded_href = url[href_start:href_end]

    # Decode URL-encoded characters
    decoded_href = encoded_href.replace("%3A", ":").replace("%2F", "/")
    parts = decoded_href.split("/")
    f_url = f'https://www.bangkokpost.com/{parts[3]}/{parts[4]}/{parts[5]}/'
    return f_url

# Function to extract article content while skipping irrelevant sections
def get_article(all_p):
    """
    Combines the content of all <p> tags in a news article while skipping
    irrelevant keywords like 'published', 'newspaper section', etc.

    Args:
        all_p (list): List of <p> tags from the article.

    Returns:
        str: Combined article content.
    """
    news_article = []
    for p_tag in all_p:
        text = p_tag.get_text(strip=True)
        if not any(keyword in text.lower() for keyword in ['published', 'newspaper section', 'writer', 'subscribing']):
            news_article.append(text)
    article_content = ' '.join(news_article)
    return article_content

# Function to analyze sentiment and perform topic modeling using OpenAI
def get_openai_SA_TM(article, stock, topic_counts, retry=3):
    """
    Performs Sentiment Analysis (SA) and Topic Modeling (TM) on an article
    for a specified stock using OpenAI's API. Retries on failure.

    Args:
        article (str): The article content.
        stock (str): Stock name to analyze.
        topic_counts (int): Number of topics to include in the result.
        retry (int): Number of retry attempts in case of failure.

    Returns:
        dict: A dictionary containing the stock's sentiment and topics.
    """
    import time  # Import time to add delay between retries

    # Expected output format for sentiment and topic modeling
    stock_format = "{stock:'a',sentiment:'x',topic:[]}"

    for attempt in range(retry):
        try:
            # Generate completion using OpenAI GPT model
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "assistant",
                        "content": f"""
    This is a news article about Thai stock {stock}. {article}
    Please identify the stock name, perform sentiment analysis, and topic modeling.
    The output should be in the format of a dictionary like this: {stock_format}.
    - sentiment = overall sentiment of the stock in the post (negative, positive, neutral—no explanation needed).
    - topic = a list of topics mentioned in the post, preferably non-neutral.

    Ensure the output is Python-viable.
    Don't include company names in the topic modelling.
    Include only {topic_counts} topics.
    Don't include ```python in the output."""
                    }
                ]
            )

            # Output response for debugging and evaluation
            print(type(completion.choices[0].message.content))
            print(completion.choices[0].message.content)

            # Evaluate and return the completion result
            return eval(completion.choices[0].message.content)

        except Exception as e:
            # Print error message and retry if applicable
            print(f"Attempt {attempt + 1} failed: {e}")

            # If all retries fail, re-raise the exception
            if attempt == retry - 1:
                raise
            else:
                # Wait before retrying
                time.sleep(2)  # 2-second delay before the next retry
