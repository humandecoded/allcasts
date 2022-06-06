## allcasts 📻 🗃


A Python script for downloading all available episodes from a podcast RSS feed. Useful for making private archives of your favourite podcasts.
This is a stripped down version of the original.
This version relies on `response.get()` as opposed to `wget` thus allowing us to pass a user-agent along with our download request. 

### Updates to Original Allcasts.py
* When downloading, Allcasts will check if that file already exists in the save directory and skip if necessary. This gives you the abillity to build it out a list of RSS feeds you would like to check periodically and end up with a well organized collection of files. 
* Now have the ability to designate saving sub-folders on a per url basis when using the `-i` option

### Command Line: Arguments

Allcasts supports a variety of command line arguments. To display help message below use `allcasts -h`

```bash
usage: allcasts.py [-h] (-f <URL> | -i <FILE>) [-d <DIRECTORY>] [-s <NUMBER>] [-e <NUMBER>] [-a] [-n <NUMBER>] [-l] [-v]

A friendly command line podcast downloader - supports downloading entire feeds, individual episodes, and a range of episodes

optional arguments:
  -h, --help            show this help message and exit
  -f <URL>, --feed <URL>
                        the url of the podcast feed
  -i <FILE>, --input <FILE>
                        the input file containing a list of podcast feeds
  -d <DIRECTORY>, --directory <DIRECTORY>
                        the directory to save the podcast episodes
  -s <NUMBER>, --start <NUMBER>
                        the number of the first episode to download
  -e <NUMBER>, --end <NUMBER>
                        the number of the last episode to download
  -a, --all             download all episodes
  -n <NUMBER>, --number <NUMBER>
                        download a specific episode
  -l, --latest          download the latest episode
  -v, --version         display the version number
```
### Batch Downloading from CSV File

When using the `-i` option you can also specify a sub-folder to place that feed in to. Just make the second field of the csv a folder name. Your csv will be structured as: `<rss feed url>, <folder name>`

You can still specify the root of your saves using `-d`

#### Example Commands

* **Download episodes 100 to 120**

```bash
allcasts -f "https://atp.fm/rss" -s 100 -e 120
```

* **Download all episodes of a podcast**

```bash
allcasts -f "https://atp.fm/rss" -a
```

* **Download episode 200**

```bash
allcasts -f "https://atp.fm/rss" -n 100
```

* **Download a list of RSS feeds**

```bash
allcasts -i "podcast_feeds.txt"
```

* **Transcribe downloaded episodes to a txt file for keyword searching**

```bash
allcasts -f "https://atp.fm/rss" -t
```
