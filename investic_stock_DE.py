from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import pandas as pd
from investic_utils import extract_BangkokPost_news, get_article, get_openai_SA_TM
from tqdm import tqdm  # Import tqdm for the loading bar
import time  # Import time for sleep functionality
import os

# Configuration
company = 'PTT'
start_date = datetime.now()
day_backward = 10
end_date = datetime.now() - timedelta(days=day_backward)
scrape_rows = 10
start = 0
topic_counts = 5
csv_path = 'csv'

# Construct URL
url = f"https://search.bangkokpost.com/search/result?start={start}&q={company}&category=news&refinementFilter=&sort=newest&rows={scrape_rows}&publishedDate="

try:
    # Request page content
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('div', class_='search-listnews--colright')
    posts = []

    # Add loading bar
    for row in tqdm(rows, desc="Processing rows"):
        # Extract publication date
        p = row.find('p', class_=False)
        if not p:
            continue
        span = p.find('span')
        if span:
            published_on = datetime.strptime(span.find('a').get_text(strip=True), "%d/%m/%Y")
            if end_date <= published_on < start_date:
                # Extract news content
                h3 = row.find('h3')
                if h3:
                    link = h3.find('a', href=True)
                    full_url = extract_BangkokPost_news(link['href'])
                    article_response = requests.get(full_url)
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    all_paragraphs = article_soup.find_all('p')
                    article = get_article(all_paragraphs)
                    
                    # Perform sentiment analysis
                    SA_TM = get_openai_SA_TM(article, company, topic_counts)
                    SA_TM['date'] = published_on
                    SA_TM['stock'] = company
                    posts.append(SA_TM)

    # Create a DataFrame
    df = pd.DataFrame(posts)
    df.to_csv(os.path.join(csv_path,company+'_'+datetime.now().strftime("%d_%m_%y_%H_%M")+'.csv'),header=True)

except requests.exceptions.RequestException as e:
    print(f"Error occurred during the request: {e}")

except ValueError:
    print("Error parsing the content.")
