#!/usr/bin/env python3


from collections import defaultdict
import tweepy
import json
import sys
import time


from keys import consumer_secret, consumer_key, access_token, access_token_secret
from data_collector_config import levels, user_name, max_followings_filter

clear_string = "          "
sleep_duration_seconds = 62 * 2.5  # second


def collect_followings_relations(starting_user_id, max_level, tweepy_api):
    stage = set()
    last_stage = {starting_user_id}
    followings = defaultdict(list)

    for level in range(max_level):
        print("level %d (%d users)" % (level, len(last_stage)), file=sys.stderr)
        new_stage = set()
        index = 0
        for user in last_stage:
            index += 1
            print(("\r\tproccessing %d of %d (%.2f%%)..." + clear_string * 3 + "\r") %
                  (index, len(last_stage), index / len(last_stage) * 100), end="", file=sys.stderr)
            sys.stderr.flush()
            user_followings = []
            while True:
                try:
                    user_followings = tweepy_api.friends_ids(user)
                except tweepy.error.RateLimitError as ex:
                    print("\n%r" % (ex), file=sys.stderr)
                    time.sleep(sleep_duration_seconds)
                    continue
                except Exception as ex:
                    print("\n%r" % (ex), file=sys.stderr)
                break
            permitted_user_followings = []
            if not max_followings_filter:
                followings[user] = user_followings
                permitted_user_followings = user_followings
            else:
                follwing_index = 0
                for following in user_followings:
                    follwing_index += 1
                    print("\r\tproccessing %d of %d (%.2f%%): following %d of %d (%.2f%%)..." %
                          (index, len(last_stage), index / len(last_stage) * 100, follwing_index, len(user_followings),
                           follwing_index / len(user_followings) * 100), end="", file=sys.stderr)
                    followings_number = max_followings_filter
                    try:
                        followings_number = tweepy_api.get_user(following).friends_count
                    except Exception as ex:
                        print("\n%r" % (ex), file=sys.stderr)
                    followings[user].append(following)
                    if followings_number < max_followings_filter:
                        permitted_user_followings.append(following)
            new_stage = new_stage.union(set(permitted_user_followings))
        stage = stage.union(last_stage)
        last_stage = new_stage.difference(stage)
        print(("\rstage size: %d" + clear_string * 6 + "\n") % (len(stage)), file=sys.stderr)

    stage = stage.union(last_stage)
    print("level %d (%d users)" % (max_level, len(last_stage)), file=sys.stderr)
    index = 0
    for user in last_stage:
        index += 1
        print(("\r\tproccessing %d of %d (%.2f%%)..." + clear_string * 3 + "\r") %
              (index, len(last_stage), index / len(last_stage) * 100), end="", file=sys.stderr)
        user_followings = []
        while True:
            try:
                user_followings = tweepy_api.friends_ids(user)
            except tweepy.error.RateLimitError as ex:
                print("\n%r" % (ex), file=sys.stderr)
                time.sleep(sleep_duration_seconds)
                continue
            except Exception as ex:
                print("\n%r" % (ex), file=sys.stderr)
            break
        follwing_index = 0
        for following in user_followings:
            follwing_index += 1
            print("\r\tproccessing %d of %d (%.2f%%): following %d of %d (%.2f%%)..." %
                  (index, len(last_stage), index / len(last_stage) * 100, follwing_index, len(user_followings),
                   follwing_index / len(user_followings) * 100), end="", file=sys.stderr)
            if following in stage:
                followings[user].append(following)
    print(("\rstage size: %d" + clear_string * 6 + "\n") % (len(stage)), file=sys.stderr)

    print("final check...", file=sys.stderr)
    index = 0
    for user in stage:
        index += 1
        print("\r\tproccessing %d of %d (%.2f%%)..." %
              (index, len(stage), index / len(stage) * 100), end="", file=sys.stderr)
        if user not in followings.keys():
            followings[user] = []

    print(("\rcollecting data completed. stage size: %d" + clear_string * 4 + "\n") % (len(stage)), file=sys.stderr)

    return (followings, stage)


def user_names_by_id(ids):
    users = {}
    for uid in ids:
        try:
            users[uid] = api.get_user(uid).screen_name
        except Exception as ex:
            print("%d : %r" % (uid, ex), file=sys.stderr)
            users[uid] = str(uid)
    return users


def translate_followings_db_ids_to_names(followings, users):
    result_db = defaultdict(list)
    for key in followings.keys():
        for value in followings[key]:
            result_db[users[int(key)]].append(users[int(value)])
    return result_db


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    if user_name:
        user = api.get_user(user_name)
    else:
        auth.set_access_token(access_token, access_token_secret)
        user = api.me()

    print("@%s (%s) :\t%d following(s)\n" % (user.screen_name, user.name, user.friends_count), file=sys.stderr)
    (followings, ids) = collect_followings_relations(user.id, levels, api)
    users = user_names_by_id(ids)

    print(json.dumps((user.screen_name, users, followings)))
