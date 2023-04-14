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
from itunes_API import ItunesAPI
import csv
from datetime import datetime

# initialise colorama (required for Windows)
col.init()


def create_podcast_dict(url):
	'''
	returns a dictionary of the podcast feed
	'''
	try:
	    print(url)
	    with urllib.request.urlopen(url) as response:
		    podcast_dict = xmltodict.parse(response.read())

	    return podcast_dict
	except:
		return "Error"

def download_episode(feed_url, directory, episode_number):
	'''
	download a specific podcast episode from the rss feed url and save it to the directory
	'''
	podcast_dict = create_podcast_dict(feed_url)
	episode_title = podcast_dict['rss']['channel']['item'][episode_number]['title']
	file_name = f"{episode_title}.mp3"
	download_episode(podcast_dict['rss']['channel']['item'][episode_number]['enclosure']['@url'], directory, file_name)		
	print(f"\n{col.Fore.GREEN}🎧 Downloaded {episode_title}{col.Fore.RESET}")
	print(f"\n{col.Fore.BLUE}--> 🎉 Podcast downloaded!{col.Fore.RESET}")

def download_episode_range(feed_url, directory, start_number, end_number):
	'''
	download a range of podcast episodes from a given rss feed url and save them to the directory
	'''
	print(f"Downloading episodes {col.Fore.GREEN}{start_number}{col.Fore.RESET} to {col.Fore.GREEN}{end_number}{col.Fore.RESET}...")
	podcast_dict = create_podcast_dict(feed_url)
	# swap values of start and end numbers if the start number is greater than the end number
	if start_number > end_number:
		start_number, end_number = end_number, start_number
	# create a list of the podcast episodes
	all_podcast_episodes = create_podcast_dict['rss']['channel']['item']
	# reverse list of episodes so that the oldest episodes are downloaded first
	all_podcast_episodes.reverse()
	# if the podcast has episode tags, use those to download the episode range
	if 'itunes:episode' in podcast_dict['rss']['channel']['item'][0]:
		for episode in all_podcast_episodes[start_number-1:end_number]:
			episode_title = episode['title']
			file_name = f"{episode_title}.mp3"
			episode_number = int(episode['itunes:episode'])
			if episode_number >= start_number and episode_number <= end_number:
				download_episode(episode['enclosure']['@url'], directory, file_name)
				print(f"\n{col.Fore.GREEN}🎧 Downloaded {episode_title}{col.Fore.RESET}")
	# if no episode tags are present, download episodes based on their order in the feed
	else:
		for episode in all_podcast_episodes[start_number-1:end_number]:
			episode_title = episode['title']
			file_name = f"{episode_title}.mp3"
			file_name = episode['enclosure']['@url'].split('/')[-1]
			# remove all text after '?' in the filename
			file_name = file_name.split('?')[0]
			download_episode(episode['enclosure']['@url'], directory, file_name)
			print(f"\n{col.Fore.GREEN}🎧 Downloaded {episode_title}{col.Fore.RESET}")

		print(f"\n{col.Fore.BLUE}--> 🎉 All podcast episodes downloaded!{col.Fore.RESET}")

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
	'''
	download all podcasts from the rss feed url and save them to the directory
	'''
	
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
				if (file_name.strip() in os.listdir(directory) or 
					podcast_title+".mp3" in os.listdir(directory)):

					print(f"{file_name} is already saved in this folder. Skipping")
				
				else:
					try:
						download_episode(item['enclosure']['@url'], directory, file_name)
					except:
						print(f"Error: Could not download {file_name}......")
						f.write(f"{directory}/{podcast_title}\n")

					print(f"\n{col.Fore.GREEN}🎧 Downloaded {podcast_title}{col.Fore.RESET} as {col.Fore.BLUE}{file_name}{col.Fore.RESET}")
			print(f"\n{col.Fore.BLUE}--> 🎉 All podcasts downloaded!{col.Fore.RESET}")
		# write feed resolve error to log
		else:
			f.write(f"Could not resolve {feed_url}\n")

def create_directory(directory):
	'''
	create the directory if it doesn't exist
	'''
	if not path.exists(directory):
		print(f"Creating directory {directory}")
		os.makedirs(directory)

def download_all_podcasts_from_file(file_path, directory):
	'''
	download all podcasts from a text file and save them to the directory
	'''
	log_name = datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + ".log"

	with open(file_path, 'r') as f:
		reader = csv.reader(f)
		rss_list = list(reader)
		for line in rss_list:
			# if now dir specified in csv, just use directory from cli
			if len(line) < 2:
				save_location = directory
			else:
				save_location = directory + line[1].strip() + "/"
			create_directory(save_location)
			download_all_episodes(feed_url = line[0].strip(), directory = save_location, log_path=directory+log_name)


def itunes_search_cli():
	'''
	promt the user to search for a podcast, choose from the results and return the URL
	'''
	search_term = pyip.inputStr(prompt='Search for a podcast: ')
	# strip whitespace from search term, concatenate each word with '+'
	search_term = '+'.join(search_term.split())
	# search for the podcast
	results = ItunesAPI.podcast_search(search_term)
	if results:
		print(f"\n{col.Fore.BLUE}--> Search results: {col.Fore.RESET}")
		for i, result in enumerate(results):
			print(f"{col.Fore.GREEN}{i+1}{col.Fore.RESET}. {result['trackName']}")
		print(f"{col.Fore.BLUE}--> Choose a podcast from the list above: {col.Fore.RESET}")
		podcast_number = pyip.inputInt(prompt='', min=1, max=len(results))
		return results[podcast_number-1]['feedUrl']
	else:
		print(f"\n{col.Fore.RED}Error: No podcasts found!{col.Fore.RESET}")
		sys.exit(1)


def main():
	'''
	The main function will check for arguments, validate them, and call the appropriate function 
	OR if no arguments are passed, it will prompt the user for the required parameters
	'''
	# if arguments are passed, parse them:
	if len(sys.argv) > 1:
		# create the parser
		parser = argparse.ArgumentParser(description="A friendly command line podcast downloader - supports downloading entire feeds, individual episodes, and a range of episodes")
		mutually_exclusive = parser.add_mutually_exclusive_group(required=True)
		# define the arguments
		mutually_exclusive.add_argument("-f", "--feed", help="the url of the podcast feed", type=str, metavar="<URL>")
		mutually_exclusive.add_argument("-i", "--input", help="the input file containing a list of podcast feeds", type=str, metavar="<FILE>")
		parser.add_argument("-d", "--directory", help="the directory to save the podcast episodes", required=False, type=str, metavar="<DIRECTORY>")
		parser.add_argument("-s", "--start", help="the number of the first episode to download", type=int, metavar="<NUMBER>")
		parser.add_argument("-e", "--end", help="the number of the last episode to download", type=int, metavar="<NUMBER>")
		parser.add_argument("-a", "--all", help="download all episodes", action="store_true", required=False)
		parser.add_argument("-n", "--number", help="download a specific episode", type=int, metavar="<NUMBER>")
		parser.add_argument("-l", "--latest", help="download the latest episode", action="store_true", required=False)
		parser.add_argument("-v", "--version", help="display the version number", action="store_true", required=False)
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
		if args.all:
			download_all_episodes(args.feed, directory)
		elif args.start and args.end:
			download_episode_range(args.feed, directory, args.start, args.end)
		elif args.number:
			download_episode_range(args.feed, directory, args.number, args.number)
		elif args.version:
			print(f"{col.Fore.BLUE}AllCasts v {col.Fore.RESET}")
		elif args.input:
			download_all_podcasts_from_file(args.input, directory)
		else:
			print(f"{col.Fore.RED}ERROR: You must specify either --all, --start, or --end{col.Fore.RESET}")
			sys.exit()
	else:
	# if no arguments are passed, prompt the user for the required information
		# display welcome message
		print(f"{col.Fore.RED}=========================================================={col.Fore.RESET}")
		print(f"{col.Fore.BLUE} ========= Welcome to the AllCasts App! ========{col.Fore.RESET}")
		print(f"{col.Fore.RED}=========================================================={col.Fore.RESET}")
		# ask if they want to search for a podcast
		mode = pyip.inputMenu(choices=['Search for a podcast','Enter URL', 'Quit'], prompt='Which would you like to do?\n', numbered=True)
		if mode == 'Search for a podcast':
			# if they want to search for a podcast, prompt the user
			feed_url = itunes_search_cli()
			download_mode = pyip.inputMenu(choices=['Download all episodes', 'Download a specific episode', 'Download an episode range', 'Quit'], prompt='Which would you like to do?\n', numbered=True)
			if download_mode == 'Download all episodes':
				download_all_episodes(feed_url, os.getcwd())
			elif download_mode == 'Download a specific episode':
				episode_number = pyip.inputInt(prompt='Enter the episode number: ')
				download_episode_range(feed_url, os.getcwd(), episode_number, episode_number)
			elif download_mode == 'Download an episode range':
				start_episode = pyip.inputInt(prompt='Enter the first episode number: ')
				end_episode = pyip.inputInt(prompt='Enter the last episode number: ')
				download_episode_range(feed_url, os.getcwd(), start_episode, end_episode)
		elif mode == 'Enter URL':
			# prompt the user for the url
			pod_url = pyip.inputURL(prompt=f'Please enter the URL of the podcast feed you want to download: ')
			# prompt the user for the directory
			download_dir = pyip.inputFilepath(prompt='Please enter the directory you want to download the podcast to [leave blank for current dir]: ', blank=True)
			# if the user didn't enter a directory, use the current directory
			if download_dir == '' or download_dir == '.':
				download_dir = path.abspath('.')
			# inform the user the downloads will begin
			print(f"Downloading all podcasts from {pod_url} to {download_dir}")
			# download the podcast
			try:
				download_all_episodes(pod_url, download_dir)
			except KeyboardInterrupt:
				sys.exit()
		sys.exit()

if __name__ == '__main__':
	main()




# todo: functionality to harvest and parse out metadata for your podcasts. Like pull in episode description