#!/usr/bin/env python3


from collections import defaultdict
import tweepy
import json
import sys


from keys import *


def collect_followings_relations(starting_user_id, max_level, tweepy_api):
    stage = set()
    last_stage = {starting_user_id}
    followings = defaultdict(list)

    for level in range(max_level):
        new_stage = set()
        for user in last_stage:
            user_followings = tweepy_api.friends_ids(user)
            followings[user] = user_followings
            new_stage = new_stage.union(set(user_followings))
        stage = stage.union(last_stage)
        last_stage = new_stage.difference(stage)
        print("level %d : stage size: %d" % (level, len(stage)), file = sys.stderr)

    stage = stage.union(last_stage)
    print("level %d : stage size: %d" % (max_level, len(stage)), file = sys.stderr)
    for user in last_stage:
        user_followings = tweepy_api.friends_ids(user)
        for following in user_followings:
            if following in stage:
                followings[user].append(following)

    for user in stage:
        if user not in followings.keys():
            followings[user] = []

    return (followings, stage)


def translate_followings_db_ids_to_names(followings, users):

    # preproccess data extarcted from json
    users = dict((int(i), users[i]) for i in users.keys())

    result_db = defaultdict(list)
    for key in followings.keys():
        for value in followings[key]:
            result_db[users[int(key)]].append(users[int(value)])
    return result_db


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True)

    user = api.me()

    print("%s (%s) :\t%d" % (user.screen_name, user.name, user.friends_count), file = sys.stderr)
    (followings, ids) = collect_followings_relations(user.id, 1, api)
    users = dict((id, api.get_user(id).screen_name) for id in ids)
    
    print(json.dumps((users, followings)))

