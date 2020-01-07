import re
import sqlite3
import time

import enchant
import praw
from praw.exceptions import APIException
from prawcore import NotFound
import privatekeys

# for perspective stuff
import json
import requests

USERNAME = privatekeys.username
PASSWORD = privatekeys.password

perspective_api_key = privatekeys.perspective_api_key

reddit = praw.Reddit(client_id=privatekeys.reddit_client_id,
                     client_secret=privatekeys.reddit_client_secret_key,
                     user_agent='console:testbot:1.0.0 (by /u/deltatwister)',
                     username=USERNAME,
                     password=PASSWORD)  # subject to change based off of username availability

subreddit = reddit.subreddit('bottesting')
keyphrase = '!testbot'

print("opening database")
sql = sqlite3.connect('sql.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
sql.commit()
d = enchant.Dict("en_US")
queued_comments = []


def is_word(word):
    return d.check(word)


def is_a_real_user(username):
    num_dogs = 0
    try:
        redditor = reddit.redditor(username)
        comments = redditor.comments.new(limit=2)
        for comment in comments:
            if "dog" in comment.body:
                num_dogs = num_dogs + 1
        return True
    except NotFound:
        return False


def analyze_user_comments(username, limit=50):
    num_dogs = 0
    try:
        redditor = reddit.redditor(username)
        comments = redditor.comments.new(limit=limit)
        for comment in comments:
            if "dog" in comment.body:
                num_dogs = num_dogs + 1
        return "\"" + username + "\" has said dog " + str(num_dogs) + " times"
    except NotFound:
        return "User \"" + username + "\" does not exist or was banned"

    # look for phrase and reply appropriately


def analyze_string_toxicity(comment):
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' +
           '?key=' + perspective_api_key)
    data_dict = {
        'comment': {'text': comment},
        'languages': ['en'],
        'requestedAttributes': {'TOXICITY': {}}
    }
    response = requests.post(url=url, data=json.dumps(data_dict))
    response_dict = json.loads(response.content)
    # print(json.dumps(response_dict, indent=2) + "\n")
    comment_json_dict = json.loads(json.dumps(response_dict, indent=2))
    try:
        comment_toxicity_rating = float(
            comment_json_dict["attributeScores"]["TOXICITY"]["summaryScore"]["value"])
    except KeyError:
        print(json.dumps(response_dict, indent=2) + "\n")
        comment_toxicity_rating = 0;
    # print(comment_toxicity_rating)
    return comment_toxicity_rating


def analyze_user_toxicity(username, limit=50):
    num_comments_analyzed = 0
    total_toxicity = 0.00
    try:
        redditor = reddit.redditor(username)
        comments = redditor.comments.new()
        for comment in comments:
            time.sleep(1.2)  # 1 qps is free from perspective api
            num_comments_analyzed = num_comments_analyzed + 1
            comment_toxicity_rating = analyze_string_toxicity(comment.body)
            total_toxicity = total_toxicity + comment_toxicity_rating
        print(str(total_toxicity) + " overall toxicity over " + str(num_comments_analyzed) + " comments")
        if num_comments_analyzed is 0:
            return username + " has not posted any comments..."
        return "According to my analysis, \"" + username + "\" has an average toxicity rating of " \
               + str(total_toxicity / num_comments_analyzed) + " between all of their comments"
    except NotFound:
        return "User \"" + username + "\" does not exist or was banned"


def testbot():
    for comment in subreddit.stream.comments():
        # time.sleep(20)
        add_to_database = True
        cid = comment.id
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [cid])
        print('checking if comment is already in database...')
        if not cur.fetchone():  # comment is not in database
            print('comment not already in database, checking for keyphrase')
            if USERNAME != comment.author.name and keyphrase in comment.body:
                print("keyphrase present!")
                word = comment.body.replace(keyphrase, '')  # removing the keyphrase from comment to pass to dictionary
                target_user = re.search('\/u\/[A-Za-z0-9_-]{3,20}', word)
                if target_user:
                    print(target_user.group(0))
                    target_username = target_user.group(0)[3:]
                    if bool(target_user) and is_a_real_user(target_username):
                        post_limit_exceeded = False
                        reply = analyze_user_toxicity(target_username)
                        try:
                            comment.reply(reply)
                            print('posted')
                        except APIException:
                            post_limit_exceeded = True
                            print('too frequent, sleeping for 20 seconds...')
                            time.sleep(20)
                        finally:
                            if post_limit_exceeded:
                                comment.reply(reply)
                                print('posted')



        if add_to_database:
            cur.execute('INSERT INTO oldposts VALUES(?)', [cid])
            sql.commit()

testbot()
