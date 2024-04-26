#! python3
'''allcasts - A friendly command line podcast downloader

allcasts allows you to batch download podcasts from a given RSS feed.
allcasts can download all episodes, a range of episodes, or a specific episode.
Get started by running allcasts with no arguments or with the --help argument.
'''

import os
import urllib
from os import path
import sys
import requests
import argparse
import colorama as col
import pyinputplus as pyip
import xmltodict
import csv
from datetime import datetime

# initialise colorama (required for Windows)
col.init()


def create_podcast_dict(url):
	
    #returns a dictionary of the podcast feed
    try:
        print(url)
        with urllib.request.urlopen(url) as response:
            podcast_dict = xmltodict.parse(response.read())

        return podcast_dict
    except:
        return "Error"

def download_episode(episode_url, directory, filename):
	
	# adding a user agent allows you to avoid 403 errors in some cases
	
	agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0','Referer':'https://your_url_or_web_addrees'} 	
	print(f"Downloading {episode_url}...")
	response = requests.get(episode_url, headers=agent, stream=True)
	if directory[-1] != "/":
		directory = directory + "/"
	
	with open(directory + filename, "wb") as f:
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)

def download_all_episodes(feed_url, directory, log_path):
	
	# download all podcasts from the rss feed url and save them to the directory
	
	
	# create a log file for errors
	with open(log_path, "a") as f:
	# create the directory if it doesn't exist
		podcast_dict = create_podcast_dict(feed_url)
		# if rss feed was able to resolve
		if podcast_dict != "Error":
			for item in podcast_dict['rss']['channel']['item']:
				podcast_title = item['title']
				# extract the publish date from rss feed
				try:
					pub_date = datetime.strftime(datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S %z"), "%Y-%m-%d")
				except ValueError:
					try:
						pub_date = datetime.strftime(datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S %Z"), "%Y-%m-%d")
					except ValueError:
						pub_date=""

				# slashes will break the file name
				podcast_title = podcast_title.replace("/", "")
				file_name = f"{pub_date} {podcast_title}.mp3"
				
				# check for existence of file in the save directory
	            # currently breaks if owner has changed case of podcast title
				if (file_name.strip().lower() in [list_file.lower() for list_file in os.listdir(directory)] or 
					podcast_title.lower() + ".mp3" in [list_file.lower() for list_file in os.listdir(directory)]):

					print(f"{file_name} is already saved in this folder. Skipping")
				
				else:
					try:
						download_episode(item['enclosure']['@url'], directory, file_name)
						f.write(f"Downloaded: {directory}{podcast_title}\n")
					except:
						print(f"Error: Could not download {file_name}......")
						f.write(f"Error: Could not download {directory}/{podcast_title}\n")

					print(f"\n{col.Fore.GREEN}🎧 Downloaded {podcast_title}{col.Fore.RESET} as {col.Fore.BLUE}{file_name}{col.Fore.RESET}")
			print(f"\n{col.Fore.BLUE}--> 🎉 All podcasts downloaded!{col.Fore.RESET}")
		# write feed resolve error to log
		else:
			f.write(f"Could not resolve {feed_url}\n")

def create_directory(directory):
	
	# create the directory if it doesn't exist

	if not path.exists(directory):
		print(f"Creating directory {directory}")
		os.makedirs(directory)

def download_all_podcasts_from_file(file_path, directory):
	
	# download all podcasts from a text file and save them to the directory
	
	log_name = datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".log"
    # read in list of rss feeds and save locations
	with open(file_path, 'r') as f:
		reader = csv.reader(f)
		rss_list = list(reader)
		# loop through each entry
		for line in rss_list:
			# if now dir specified in csv, just use directory from cli
			if len(line) < 2:
				save_location = directory
			else:
				save_location = directory + line[1].strip() + "/"
			create_directory(save_location)
			download_all_episodes(feed_url = line[0].strip(), directory = save_location, log_path=directory+log_name)


def main():
	'''
	The main function will check for arguments, validate them, and call the appropriate function 
	OR if no arguments are passed, it will prompt the user for the required parameters
	'''
	# if arguments are passed, parse them:
	if len(sys.argv) > 1:
		# create the parser
		parser = argparse.ArgumentParser(description="A friendly command line podcast downloader - supports downloading entire feeds, individual episodes, and a range of episodes")
		# define the arguments
		parser.add_argument("-i", "--input", help="the input file containing a list of podcast feeds", required=True, type=str, metavar="<FILE>")
		parser.add_argument("-d", "--directory", help="the directory to save the podcast episodes", required=False, type=str, metavar="<DIRECTORY>")
		
		args = parser.parse_args()
		if args.directory:
			if not path.isdir(args.directory):
			# check if the directory argument is valid
				print(f"{col.Fore.RED}ERROR: The directory {args.directory} does not exist.{col.Fore.RESET}")
				sys.exit()
			else:
				directory = args.directory
				if directory[-1] != "/":
					directory = directory + "/"
		# if no directory is specified, use the current working directory
		else:
			directory = os.getcwd() + "/"
		
		if args.input:
			download_all_podcasts_from_file(args.input, directory)
		else:
			print(f"{col.Fore.RED}ERROR: You must specify either --all, --start, or --end{col.Fore.RESET}")
			sys.exit()
	
if __name__ == '__main__':
	main()




# todo: functionality to harvest and parse out metadata for your podcasts. Like pull in episode description