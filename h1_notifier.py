import feedparser
import requests
import re
from bs4 import BeautifulSoup
import schedule
import time
import random
from datetime import datetime
import logging

logging.basicConfig(filename='script_output.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# CONFIG
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token="
last_sent_tweet_pubdate = None  # Add a global variable

def get_link_description(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        meta_title_element = soup.find('meta', {'name': 'description'})
        
        if meta_title_element and 'content' in meta_title_element.attrs:
            description = meta_title_element['content'].replace('#', '')
        else:
            description = 'No Description Found'

        return description
    except Exception as e:
        logging.info(f"Error getting description for {url}: {e}")
        return None

def send_to_dingtalk(content, title):
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": content},
    }
    requests.post(DINGTALK_WEBHOOK, headers=headers, json=data)

def get_new_published_tweets(feed, last_sent_tweet_pubdate):
    new_published_tweets = []

    for entry in feed.entries:
        tweet_pubdate = datetime.strptime(entry.published.replace("GMT", "+0000"), '%a, %d %b %Y %H:%M:%S %z')
        if last_sent_tweet_pubdate is None or tweet_pubdate > last_sent_tweet_pubdate:
            new_published_tweets.append(entry)
        else:
            break

    return new_published_tweets

def process_tweet(url_list):
    global last_sent_tweet_pubdate
    # random rss_url
    random.shuffle(url_list)
    for url in url_list:
        feed = feedparser.parse(url)
        if len(feed.entries) > 0:
            new_published_tweets = get_new_published_tweets(feed, last_sent_tweet_pubdate)
            if new_published_tweets:
                for entry in new_published_tweets:
                    tweet_text = entry.title
                    url_link = re.search(r'https://hackerone\.com/reports/\d+', tweet_text)
                    if url_link:
                        # Convert the link in the tweet to MarkDown format to support mobile access.
                        tweet_text = tweet_text.replace(url_link.group(), f"[{url_link.group()}]({url_link.group()})")
                        logging.info(f"RSS URL used: {url}, Latest tweet: {tweet_text[:30]}, Time: {last_sent_tweet_pubdate}")
                        tweet_pubdate = datetime.strptime(entry.published.replace("GMT", "+0000"), '%a, %d %b %Y %H:%M:%S %z')
                        hackerone_url_match = re.search(r'https://hackerone\.com/reports/\d+', tweet_text)
                        hackerone_url = hackerone_url_match.group()
                        link_description = get_link_description(hackerone_url)
                        if link_description:
                            content = f"**Tweet:** \n\n{tweet_text}\n\n**Description:**\n\n {link_description}\n\n"
                            send_to_dingtalk(content, link_description)
                        last_sent_tweet_pubdate = max(last_sent_tweet_pubdate, tweet_pubdate) if last_sent_tweet_pubdate else tweet_pubdate
                    else:
                        logging.info(f"Tweet does not contain hackerone.com, skipping, Time: {last_sent_tweet_pubdate}")
            else:
                logging.info(f"Tweet has already been sent, skipping, Time: {last_sent_tweet_pubdate}")
            break
    else:
        logging.info("Unable to get valid RSS data from all provided URLs.")


def main():
    global last_sent_tweet_pubdate
    TWITTER_USER = 'disclosedh1'

    TWITTER_RSS_URLS = [
        f"https://nitter.net/{TWITTER_USER}/rss",
        #f"https://nitter.unixfox.eu/{TWITTER_USER}/rss",
        f"https://nitter.snopyta.org/{TWITTER_USER}/rss",
        f"https://twitter.owacon.moe/{TWITTER_USER}/rss",
    ]

    logging.info("Checking for new tweets...")
    process_tweet(TWITTER_RSS_URLS)
    
    schedule.every(10).minutes.do(process_tweet, TWITTER_RSS_URLS)

    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == '__main__':
    main()
