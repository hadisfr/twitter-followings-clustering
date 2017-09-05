#!/usr/bin/env python3


import tweepy
import json
import sys


from keys import *


if __name__ == '__main__':
    users = json.loads(input())[1]
    users = dict((int(key), users[key]) for key in users.keys())

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True)

    followings = dict()
    for user_id in users.keys():
        try:
            print(users[user_id], end = " ", file = sys.stderr)
            followings[user_id] = api.get_user(user_id).friends_count
            print(followings[user_id], file = sys.stderr)
        except Exception as ex:
            print(ex, file = sys.stderr)

    print(json.dumps((users, followings)))

