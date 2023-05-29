import openai
from secrets import *
import praw
from datetime import datetime
from tqdm import tqdm

def analyze_sentiment(text:str) -> int:
  openai.api_key = OPENAI_API_KEY
  response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
    messages=[
          {"role": "user", "content": "You are a sentiment claissifier of the following text on a scale of 1 to 10. respond only the number"},
          {"role": "assistant", "content": "ok"},
          {"role": "user", "content": text},
      ],
    temperature=0,
    max_tokens=6,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  answer=response.choices[0].message.content
  return int(answer) if answer.isdigit() else -1
  
def get_subreddit_posts(subreddit : str, limit:int) -> list:
  reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_SECRET_KEY, user_agent='scraper 1.0 algo-project')
  posts = []
  for post in reddit.subreddit(subreddit).new(limit=limit):
    #check if post is a text post and not a meme, and not a daily discussion thread
    if post.link_flair_text != 'Meme' and "Daily Discussion Thread" not in post.title:
      #encode-decode will remove emojis from the title
      title=post.title.encode('ascii', 'ignore').decode()
      posts.append(title)

      #If we will need dates to backtest:
      #posted_date = datetime.utcfromtimestamp(post.created_utc)
    
  return posts  
  
def get_reddit_stock_posts(stock:str, limit:int)->list:
  reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_SECRET_KEY, user_agent='scraper 1.0 algo-project')
  posts=[]
  for post in reddit.subreddit('all').search(stock, limit=limit):
    #check if post is a text post and not a meme, and not a daily discussion thread
    if post.link_flair_text != 'Meme' and "Daily Discussion Thread" not in post.title:
      #encode-decode will remove emojis from the title
      title=post.title.encode('ascii', 'ignore').decode()
      posts.append(title)
      
      #If we will need dates to backtest:
      #posted_date = datetime.utcfromtimestamp(post.created_utc)
    
def main():
  stocks=['TESLA'  ,'GOOGLE','MICROSOFT','APPLE']
  posts=get_subreddit_posts(subreddit="wallstreetbets", limit=500)
  #keep only posts that contain the stock name
  for post in posts:
    if any(stock in post.upper() for stock in stocks):
      print(post)#,'   ',analyze_sentiment(post))
  
  
  
if __name__ == "__main__":
  main()
