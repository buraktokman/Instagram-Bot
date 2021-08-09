#!/usr/bin/env python3
# coding=utf-8
'''
#-------------------------------------------------------------------------------
Project		: Instagram Bot
Module		: follow
Purpose   	: Follow users, like posts, upload photo, unfollow
Version		: 0.1.2 beta
Status 		: Development

Modified	: 2021 Feb 22
Created   	: 2019 Nov 03
#-------------------------------------------------------------------------------
'''
from pathlib import Path
from instapy_cli import client
from instapy import InstaPy
from instapy import smart_run
from colorama import Fore, Back, Style
import instapy
import os
import sys
import random
import time
import json
import threading
sys.path.insert(0, str(Path(Path(__file__).parents[0] / 'lib')))
import logz



# # # # # # # # # # # # # # # # #
#
#	CONFIG
#
DIR = str(Path(__file__).parent.absolute())
CONFIG = {
			'comments' : ['✌️ Stay positive @{}', u'🍀 @{}', u'🥰 @{}', u'❤️ @{}'],
			# 'similar_accounts': ["she.has.acne", "acneisajourney", "aves.skin", "myadultacnejourney", "iz.beyondthesurface", "acnefreedream", "yourskinisart", "averelacne", "acne_journey_20", "laurasskindiary", "zita.on.inerta", "anotheracne.story", "roaccutaniek", "caitlinskinpositivity", "postpilljorney", "ladypimpleton", "allskinisnormal", "skin_byjordan", "acneselfhelp", "acnelifewithlaura", "journey_with_megan", "acne.baby", "worthyinmyskin", "lifeinmy.skin", "skin.postive.lauren"],
			# 'hashtags': ["pimplepopper", "acneproblems", "acnecommunity", "acnejourney", "acnepositivity", "acneprone", "adultacne", "acnecare", "acneproneskin", "skinpositivity", "accutane", "skinpositive"],
			# 'follow-interval': 24, # hours
			'accounts_file': DIR + '/accounts.json',
			'hashtags_file': DIR + '/hashtags.txt',
			'similar_accounts_file': DIR + '/similar_accounts.txt',
			'comments_file': DIR + '/comments.txt',
			}



# # # # # # # # # # # # # # # # #
#
#	BOT
#
def follow():
	global CONFIG, IG_ACCOUNTS, HASHTAGS

	print(f"{logz.timestamp()}{Fore.MAGENTA} BOT → IG account={Style.RESET_ALL}{IG_ACCOUNTS[0]['username']}")
	""" Quickstart script for InstaPy usage """

	# Get an InstaPy session!
	# set headless_browser=True to run InstaPy in the background
	session = InstaPy(username=IG_ACCOUNTS[0]['username'],
					  password=IG_ACCOUNTS[0]['password'],
					  #proxy_username='',
					  #proxy_password='',
					  #proxy_address='8.8.8.8',
					  #proxy_port=8080,
					  headless_browser=False,
					  disable_image_load=True,
					  bypass_security_challenge_using='email')

	""" Activity flow """
	with smart_run(session):
		# General settings
		session.set_relationship_bounds(enabled=True,
										delimit_by_numbers=True,
										min_posts=10,
										max_followers=1500,		# 4590
										min_followers=50,
										# max_following=0
										min_following=75,
										# potency_ratio=1.0 # followers / following
										)

		# DON'T INCLUDE
		session.set_dont_include(["friend1", "friend2"])
		session.set_dont_like(["clinic", "ship", "shop", "here", "worldwide"]) #store

		# SKIP LANGUAGES
		session.set_mandatory_language(enabled=True, character_set='LATIN')

		# SKIP
		session.set_skip_users(skip_private=True,
								skip_no_profile_pic=True,
								skip_business=True,
								skip_business_categories=['Consulting Agency', 'Advertising/Marketing', 'Business & Utility Services'], # 'Creators & Celebrities',
								# https://github.com/InstaPy/instapy-docs/blob/master/BUSINESS_CATEGORIES.md
								# dont_skip_business_categories=['Creators & Celebrities']
								)

		# ACTIVITY
		session.set_user_interact(amount=1, randomize=True, percentage=100) # media='Photo'

		# FOLLOW
		# Similar accounts

		session.follow_user_followers(CONFIG['similar_accounts'],
                                  amount=10,
                                  randomize=True, sleep_delay=600,
                                  interact=True)
		# Follow 50% of the users from the images
		session.set_do_follow(enabled=True, percentage=50, times=1)	# IG limit is 300

		# LIKE
		# ~70% of the viewed posts
		session.set_do_like(enabled=True, percentage=60)	# IG limit is 900
		# session.like_by_tags(HASHTAGS, amount=random.randint(1, 10))

		# COMMENT
		# Comment 15% of images
		session.set_do_comment(enabled=True, percentage=15)	# IG limit is 60
		session.set_comments(CONFIG['comments']) # media='Photo'

		# UNFOLLOW
		session.unfollow_users(amount=random.randint(20, 80),
								instapy_followed_enabled=True,
								instapy_followed_param="all",
								style="FIFO",
								unfollow_after=60*60*24*5,		# Unfollow after 7 days
								sleep_delay=501)

		# BOT LIMITS
		# session.set_quota_supervisor(enabled=True,
		# 								peak_follows=(56, 660),
		# 								peak_unfollows=(49, 550) sleep_after=["follows_h", "unfollows_d"],
		# 								stochastic_flow=True,
		# 								notify_me=True)
		session.set_quota_supervisor(enabled=True,
										sleep_after=["likes", "comments", "follows", "server_calls"],
										sleepyhead=True,
										stochastic_flow=True,
										notify_me=True,
										peak_likes_hourly=30,
										peak_likes_daily=150,		# 250
										peak_comments_hourly=5,
										peak_comments_daily=30,		# 30
										peak_follows_hourly=10,		# 30
										peak_follows_daily=180,		# 150
										peak_unfollows_hourly=50,
										peak_unfollows_daily=200,
										peak_server_calls_hourly=200,
										peak_server_calls_daily=2500)

		# END
		session.end()

	# Return
	return True




# # # # # # # # # # # # # # # # #
#
#	THREAD FUNC
#
def thread_follow():
	global CONFIG
	while True:
		r = follow()
		time.sleep(60 * 60 * CONFIG['follow-interval'])


# # # # # # # # # # # # # # # # #
#
#	MAIN
#
def main():
	global IG_ACCOUNTS, CONFIG, HASHTAGS
	print(f"{logz.timestamp()}{Fore.MAGENTA} INIT → {Style.RESET_ALL}Starting threads")


	# LOAD IG ACCOUNTS  --------------------------------------------
	try:
		with open(CONFIG['accounts_file'], 'r') as file:
			data = file.read().replace('\n', '')
		IG_ACCOUNTS = json.loads(data)['accounts']
	except Exception as e:
		raise e


	# LOAD HASHTAGS  ------------------------------------------------
	try:
		with open(CONFIG['hashtags_file']) as f:
			HASHTAGS = f.read().splitlines()
		random.shuffle(HASHTAGS)
	except Exception as e:
		raise e


	# LOAD COMMENTS  ------------------------------------------------
	# try:
	# 	with open(CONFIG['comments_file']) as f:
	# 		CONFIG['comments'] = f.read().splitlines()
	# except Exception as e:
	# 	raise e

	# LOAD SIMILAR ACCOUNTS  ----------------------------------------
	try:
		with open(CONFIG['similar_accounts_file']) as f:
			CONFIG['similar_accounts'] = f.read().splitlines()
		random.shuffle(CONFIG['similar_accounts'])
	except Exception as e:
		raise e


	# START
	t3 = threading.Thread(name='T1-follow', target=thread_follow)
	t3.start()


if __name__ == '__main__':
	main()