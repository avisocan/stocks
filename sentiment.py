import json
import requests
import twint
import datetime
import csv
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()
def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    text = regrex_pattern.sub(r'',text)
    return text

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score['neg'], score['neu'], score['pos']

now = datetime.datetime.now()
now=now-datetime.timedelta(hours=15)
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

while True:
    now2 = datetime.datetime.now()
    time_for_file = now.strftime("%Y-%m-%d_%H-%M-%S.csv")
    lookup_ticker = input("Enter ticker to search, enter space to quit: ")
    lookup_ticker = lookup_ticker.replace('$', '').upper()
    if lookup_ticker ==' ':
        break
    filename = lookup_ticker+'_'+time_for_file
    print("Ticker: $"+lookup_ticker)
    tweets = []
    
    c = twint.Config()
    c.Search = ('$'+lookup_ticker)
    c.Limit = 3000
    c.Output=filename
    c.Store_csv = 'true'
    c.Since = current_time
    c.Hide_output = True
    twint.run.Search(c)
    print("Tweets stored in: "+filename)
    tweets = []
    current_tweet = 0
    true_tweets = 0
    usernames = {}
    with open(filename, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for rows in reader:
            if current_tweet>0:
                entry = deEmojify(rows[8])
                if entry in usernames.keys():
                    if len(usernames[entry])<=5:
                        entry2 = deEmojify(rows[10])
                        if entry2.count("$") < 4 and entry2.upper().count(('$'+lookup_ticker).upper())>=1:
                            true_tweets+=1
                            usernames[entry].append(entry2)
                            #print(entry2)
                else:
                    entry2 = deEmojify(rows[10])
                    if entry2.count("$") < 4 and entry2.upper().count(('$'+lookup_ticker).upper())>=1:
                        true_tweets+=1
                        usernames[entry]=[entry2]
                        #print(entry2)

            current_tweet+=1
    
    bearish = 0
    bullish = 0
    none = 0
    print("Processed %d tweets, %d tweets omitted for ticker spam/username pump"%(current_tweet-1, current_tweet-1-true_tweets))
    for key in usernames:
        for tweet in usernames[key]:
            tweets.append(tweet)
            #print(key)
            #print(tweet)
    '''
    for current_message in stock_json['messages']:
        if isinstance(current_message['entities']['sentiment'], dict):
            if current_message['entities']['sentiment']['basic'] == 'Bullish':
                bullish+=1
            else:
                bearish+=1   
        else:
            none+=1
    print("Bullish: %d, Bearish: %d, None: %d" % (bullish, bearish, none))
    '''
    print("Analyzing tweets")
    negative = 0
    neutral = 0
    positive = 0
    vader_scores = []
    for tweet in tweets:
        vader_scores.append(sentiment_analyzer_scores(tweet))
    
    neg_scores = 0
    neu_scores = 0
    pos_scores = 0
    for scores in vader_scores:
        negative+=scores[0]
        neutral+=scores[1]
        positive+=scores[2]
        #print(scores)
        if scores[1]>.8:
            neu_scores+=1
        elif scores[0] >= scores[2]:
            neg_scores+=1
        elif scores[2] > scores[0]:
            pos_scores+=1
        
    print("Sums: Negative: %f, Neutral: %f, Positive: %f" % (negative, neutral, positive))
    print("Number of: Negative: %d, Neutral: %d, Positive: %d" % (neg_scores, neu_scores, pos_scores))

        
