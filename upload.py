#!/usr/bin/env python3
# coding=utf-8
'''
#-------------------------------------------------------------------------------
Project		: Instagram Bot
Module		: bot
Purpose   	: Follow users, like posts, upload photo, unfollow
Version		: 0.1.2 beta
Status 		: Development

Modified	: 2020 Jun 28
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


SCRIPT_DIR = str(Path(__file__).parent.absolute())
CONFIG = {	'upload-interval': 6, # hours
			'accounts_file': SCRIPT_DIR + '/accounts.json',
			'uploaded_file': SCRIPT_DIR + '/uploaded.txt',
			'history_file': SCRIPT_DIR + '/history.txt',
			'quotes_file': SCRIPT_DIR + '/quotes.txt',
			# CREDENTIALS
			#'username': 'morellanasel',
			#'password': 'JFN_8365ldbybdv',
			#'cookie_file': 'morellanasel_ig.json',
			}

def upload():
	global CONFIG, IG_ACCOUNTS, SCRIPT_DIR, QUOTES
	# SELECT IG ACCOUNT

	for account in IG_ACCOUNTS:
		print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → ACCOUNT → {Style.RESET_ALL}{account['username']}")

		#
		# LOAD PHOTOS / VDEOS
		#
		# Image folder
		media_dir =  SCRIPT_DIR + '/' + 'accounts/' + account['username'] + '/upload'
		# media_dir =  str(Path(Path(__file__).parents[0] / 'accounts' / account['username'] )) # "__file__"
		# media_dir = str(Path(Path(os.path.dirname(os.path.realpath('__file__'))).parents[0] / 'upload'))
		medias = []
		for file in os.listdir(media_dir):
			if file.endswith(".jpg") or file.endswith(".mp4"):
				medias.append(os.path.join(media_dir, file))

		#
		# SELECT RANDOM MEDIA
		#
		try:
			media_path = random.choice(medias)
		except Exception as e:
			print(f"{logz.timestamp()}{Fore.RED} ERROR → UPLOAD → No file found{Style.RESET_ALL}")
			return False

		# media_path = medias[-1]
		print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → MEDIA → {Style.RESET_ALL}{media_path.split('/')[-1]}")
		# Find JSON file for post text
		json_found = False
		media_id = media_path.split('/')[-1].replace('.jpg', '').replace('.mp4', '')
		for file in os.listdir(media_dir):
			if file.endswith(".json") and media_id in file:
				json_found = True
				break

		#
		# READ MEDIA CAPTION FROM .JSON
		#
		if json_found:
			try:
				with open(media_dir + '/' + file, 'r') as file:
					data = file.read().replace('\n', '')
				json_data = json.loads(data)
				# Read post text
				post_txt_temp = json_data['edge_media_to_caption']['edges'][0]['node']['text']
				# Remove mention & hashtag
				post_txt = ''
				# if '#' in post_txt_temp or '@' in post_txt_temp: # '@' in post_txt_temp or 'xenia' in post_txt_temp.lower()
				# 	post_txt_temp = post_txt_temp.split(' ')
				# 	for word in post_txt_temp:
				# 		# if '@' in word or 'xenia' in word:
				# 		if 'aloyoga' in word:
				# 			continue
				# 		else:
				# 		# if '@' not in word or 'xenia' not in word.lower():
				# 			post_txt = post_txt + ' ' + word + ' '
				# else:
				# 	post_txt = post_txt_temp
				post_txt = post_txt_temp
				# Trim
				# post_txt = post_txt_temp
				post_txt = post_txt.replace('  ',' ')
				post_txt = post_txt.rstrip().lstrip()

				# Credit OP
				# try:
				# 	post_txt = f"{post_txt}\n\nCredit @{json_data['owner']['username']}"
				# except Exception as e:
				# 	print(f"{logz.timestamp()}{Fore.YELLOW} WARNING → UPLOAD → {Style.RESET_ALL}Cannot credit user\n{e}")

				# Select random quote
				# post_txt = random.choice(QUOTES)

				# Add Hashtags
				post_txt = f'{post_txt}\n\n#yoga #fitness #meditation #yogainspiration #yogapractice #love #yogalife #yogaeverydamnday #yogi #yogateacher #namaste #yogalove #pilates #yogaeveryday #mindfulness #workout #gym #yogagirl #wellness #health #motivation #yogaeverywhere #yogachallenge #yogini #yogapose #healthylifestyle #nature #fitnessmotivation #asana #bhfyp'

				print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → TEXT → {Style.RESET_ALL}{post_txt[:20]}")
			except Exception as e:
				post_txt = None
				print(f"{logz.timestamp()}{Fore.YELLOW} WARNING → UPLOAD → JSON file not found\n{e}{Style.RESET_ALL}")
				# raise e
		else:
			post_txt = ''


		#
		# UPLOAD
		#
		uploaded = True
		print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → {Style.RESET_ALL}Uploading...")
		try:
			with client(username=account['username'],
						password=account['password'],
						cookie_file=SCRIPT_DIR + '/accounts/' + account['username'] + '/' + account['username'] + '_ig.json',
						write_cookie_file=True) as cli:

				# Generate Cookie
				cookies = cli.get_cookie()

				# # Upload with post text
				if post_txt != '':
					cli.upload(media_path, post_txt)
				else:
					cli.upload(media_path)
				cli.upload(media_path)
			uploaded = True
			print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → {Style.RESET_ALL}Uploaded")
		except Exception as e:
			uploaded = False
			print(f"{logz.timestamp()}{Fore.RED} ERROR → UPLOAD → {e}{Style.RESET_ALL}")

		#
		# MOVE TO 'UPLOADED' FOLDER
		#
		if uploaded:
			account_dir = media_dir.split('/upload')[0]
			media_name = media_path.split('/')[-1] #.replace('.png', '').replace('.mp4', '')
			json_name = media_path.split('/')[-1].replace('.png', '').replace('.mp4', '').replace('.jpg', '') + '.json'

			#print(f'media dir > {media_dir}') # /upload
			# print(f'file name including JSON, exc. path  > {file}') # /xxx.json
			#print(f'media full path > {media_path}') # /.../upload/xxx.png
			#print(f'account_dir > {account_dir}')

			if json_found:
				try:
					path_json_current = media_dir + '/' + json_name
					path_json_new = account_dir + '/uploaded/' + json_name
					os.rename(path_json_current, path_json_new)
					print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → {Style.RESET_ALL}JSON file moved to uploaded folder")
				except Exception as e:
					print(f"{logz.timestamp()}{Fore.RED} ERROR → UPLOAD → Cannot move JSON file{Style.RESET_ALL}\n{e}")
					# raise e



			try:
				media_path_new = account_dir + '/uploaded/' + media_path.split('/')[-1]
				os.rename(media_path, media_path_new)
				print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → {Style.RESET_ALL}Media file moved to uploaded folder")
			except Exception as e:
				print(f"{logz.timestamp()}{Fore.RED} ERROR → UPLOAD → Cannot move Media file{Style.RESET_ALL}\n{e}")
				# raise e

			#
			# ADD TO HISTORY
			#
			with open(CONFIG['history_file'], 'a+') as f:
				f.write(media_name + '\n')

		#print(f"{logz.timestamp()}{Fore.RED} CAUTION → SKIPPING NEXT ACCOUNT{Style.RESET_ALL}")
		#break

	# Return
	return True

def thread_upload():
	global CONFIG
	while True:
		r = upload()
		print(f"{logz.timestamp()}{Fore.MAGENTA} UPLOAD → {Style.RESET_ALL}Next upload in {CONFIG['upload-interval']} hours\n---")
		time.sleep(60 * 60 * CONFIG['upload-interval'])

def main():
	global IG_ACCOUNTS, CONFIG, QUOTES
	print(f"{logz.timestamp()}{Fore.MAGENTA} INIT → {Style.RESET_ALL}Starting threads")

	# Loading IG Accounts
	try:
		with open(CONFIG['accounts_file'], 'r') as file:
			data = file.read().replace('\n', '')
		json_data = json.loads(data)
		# Read file
		IG_ACCOUNTS = json_data['accounts']
	except Exception as e:
		post_txt = None
		raise e

	# Load Quotes
	try:
		with open(CONFIG['quotes_file']) as f:
			content = f.readlines()
		# you may also want to remove whitespace characters like `\n` at the end of each line
		QUOTES = [x.strip() for x in content]
	except Exception as e:
		QUOTES = None
		raise e

	# Shuffle
	random.shuffle(QUOTES)

	# Uploader
	t1 = threading.Thread(name='T1-uploader', target=thread_upload)
	t1.start()


if __name__ == '__main__':
	main()