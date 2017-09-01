#!/usr/bin/env python3


from collections import defaultdict
import tweepy
import json
import sys
import time


from keys import *
sleep_duration_seconds = 60 # second
levels = 1
user_name = ""


def collect_followings_relations(starting_user_id, max_level, tweepy_api):
    stage = set()
    last_stage = {starting_user_id}
    followings = defaultdict(list)

    for level in range(max_level):
        print("level %d (%d users)" % (level, len(last_stage)), file = sys.stderr)
        new_stage = set()
        index = 0
        for user in last_stage:
            index += 1
            print("\r\tproccessing %d of %d (%.2f%%)..." % (index, len(last_stage), index / len(last_stage) * 100), end = "", file = sys.stderr)
            sys.stderr.flush()
            while True:
                try:
                    user_followings = tweepy_api.friends_ids(user)
                except Exception as ex:
                    print("\r%r" % (ex), file = sys.stderr)
                    time.sleep(sleep_duration_seconds)
                    continue
                break
            followings[user] = user_followings
            new_stage = new_stage.union(set(user_followings))
        stage = stage.union(last_stage)
        last_stage = new_stage.difference(stage)
        print("\r\t                                       \rstage size: %d\n" % (len(stage)), file = sys.stderr)

    stage = stage.union(last_stage)
    print("level %d (%d users)" % (max_level, len(last_stage)), file = sys.stderr)
    index = 0
    for user in last_stage:
        index += 1
        print("\r\tproccessing %d of %d (%.2f%%)..." % (index, len(last_stage), index / len(last_stage) * 100), end = "", file = sys.stderr)
        while True:
            try:
                user_followings = tweepy_api.friends_ids(user)
            except Exception as ex:
                print("\r%r" % (ex), file = sys.stderr)
                time.sleep(sleep_duration_seconds)
                continue
            break
        for following in user_followings:
            if following in stage:
                followings[user].append(following)
    print("\r\t                                       \rstage size: %d\n" % (len(stage)), file = sys.stderr)

    print("final check...", file = sys.stderr)
    index = 0
    for user in stage:
        index += 1
        print("\r\tproccessing %d of %d (%.2f%%)..." % (index, len(stage), index / len(stage) * 100), end = "", file = sys.stderr)
        if user not in followings.keys():
            followings[user] = []

    print("\r\t                                       \rcollecting data completed. stage size: %d\n" % (len(stage)), file = sys.stderr)

    return (followings, stage)


def translate_followings_db_ids_to_names(followings, users):
    result_db = defaultdict(list)
    for key in followings.keys():
        for value in followings[key]:
            result_db[users[int(key)]].append(users[int(value)])
    return result_db


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True)

    if user_name:
        user = api.get_user(user_name)
    else:
        user = api.me()

    print("@%s (%s) :\t%d following(s)\n" % (user.screen_name, user.name, user.friends_count), file = sys.stderr)
    (followings, ids) = collect_followings_relations(user.id, levels, api)
    users = dict((id, api.get_user(id).screen_name) for id in ids)
    
    print(json.dumps((user.screen_name, users, followings)))

