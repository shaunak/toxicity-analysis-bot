import re
import sqlite3
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
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' +
           '?key=' + perspective_api_key)

    num_comments_analyzed = 0
    total_toxicity = 0.00
    try:
        redditor = reddit.redditor(username)
        comments = redditor.comments.new(limit=limit)
        for comment in comments:
            num_comments_analyzed = num_comments_analyzed + 1
            comment_toxicity_rating = analyze_string_toxicity(comment.body)
            total_toxicity = total_toxicity + comment_toxicity_rating
        print(str(total_toxicity) + " overall toxicity over " + str(num_comments_analyzed) + " comments")
        return "According to my analysis, \"" + username + "\" has an average toxicity rating of " \
               + str(total_toxicity / num_comments_analyzed) + " between all of their comments"
    except NotFound:
        return "User \"" + username + "\" does not exist or was banned"


def testbot():
    for comment in subreddit.stream.comments():
        add_to_database = True
        cid = comment.id
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [cid])
        print('checking if comment is already in database...')
        if not cur.fetchone():  # comment is not in database
            print('comment not already in database, proceeding to do action on user...')
            if USERNAME != comment.author.name and keyphrase in comment.body:
                word = comment.body.replace(keyphrase, '')  # removing the keyphrase from comment to pass to dictionary
                target_user = re.search('\/u\/[A-Za-z0-9_-]{3,20}', word)
                if target_user:
                    print(target_user.group(0))
                    target_username = target_user.group(0)[3:]
                    if bool(target_user) and is_a_real_user(target_username):
                        try:
                            reply = analyze_user_toxicity(target_username)
                            comment.reply(reply)
                            print('posted')
                        except APIException:
                            add_to_database = False
                            print('too frequent')
        if add_to_database:
            cur.execute('INSERT INTO oldposts VALUES(?)', [cid])
            sql.commit()


testbot()

