#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
Project		: Instagram Bot
Module		: logz
Purpose   	: Logging
Version		: 0.1.7 beta
Status 		: Development

Modified	: 2020 Mar 04
Created   	: 2020 Mar 04
Author		: Burak Tokman
Email 		: buraktokman@hotmail.com
Copyright 	: 2020, Bulrosa OU
Licence   	: EULA
			  Unauthorized copying of this file, via any medium is strictly prohibited
			  Proprietary and confidential
#-------------------------------------------------------------------------------
'''
from datetime import datetime
from pathlib import Path
from colorama import Fore, Back, Style
import time
import math
import logging

now = datetime.utcnow()

def timestamp():
	"""Returns current time in UTC (Coordinated Universal Time)
	"""
	now = datetime.utcnow()
	# output = '%.2d:%.2d:%.2d' % ((now.hour + 3) % 24, now.minute, now.second)
	output = f"{Fore.BLACK}[{now.strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL}"
	# Return
	return output

def unix_to_human(unix):
	"""Convert UNIX time to human readable
	"""
	human = datetime.utcfromtimestamp(int(unix)).strftime('%Y-%m-%d %H:%M:%S')
	return human

def main():
	# s = time_ago(1545791888)
	print(timestamp())

if __name__ == '__main__':
	# Main
	main()