from bs4 import BeautifulSoup
import requests
import urllib.request as urllib2
import json

import argparse
import re

import sys

import pdb

_URL_API = "https://api.genius.com/"
_URL_SEARCH = "search?q="

def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")

def getSongsFromWeb(download_list, api_token, download_dir):
    with open(download_list) as file:
        for song in file:
            getSongFromWeb(song.strip(), api_token, download_dir)

def getArtistIDAndNameFromMostPopular(search_term, client_access_token):
    querystring = _URL_API + _URL_SEARCH + urllib2.quote(search_term)
    request = urllib2.Request(querystring)
    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")
    response = urllib2.urlopen(request, timeout=3)
    encoding = response.info().get_content_charset('utf-8')
    json_obj = json.loads(response.read().decode(encoding))
    song_info = json_obj['response']['hits'][0]['result']
    artist_id = song_info['primary_artist']['id']
    artist_name = song_info['primary_artist']['name']
    return artist_id,artist_name

def listSongsFromArtistID(artist_id):
    querystring = _URL_API + "artists/" + urllib2.quote(str(artist_id)) + "/songs/"
    request = urllib2.Request(querystring)
    client_access_token = api_token
    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")
    print(querystring)
    response = urllib2.urlopen(request, timeout=3)
    encoding = response.info().get_content_charset('utf-8')
    json_obj = json.loads(response.read().decode(encoding))
    return json_obj['response']['songs']
    
def downloadSongFromURL(url, download_dir):
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html.parser")
    lyrics = html.find("div", class_="lyrics").get_text()
    song_artist = html.find("a", class_="header_with_cover_art-primary_info-primary_artist").get_text()
    song_title =  html.find("h1", class_="header_with_cover_art-primary_info-title").get_text()
    song_artist = re.sub(r'[^A-Za-z]', '', song_artist).lower()
    song_title = re.sub(r'[^A-Za-z]', '', song_title).lower()
    fn = download_dir + '/' + make_safe_filename(song_artist) + "-" + make_safe_filename(song_title) + ".txt"
    with open(fn, 'w') as file:
        lines = lyrics.split("\n")
        for line in lines:
            file.write(lyrics.encode('cp850', errors='replace').decode('cp850') + "\n")

def getSongFromWeb(search_term, api_token, download_dir): 
    artist_id,artist_name = getArtistIDAndNameFromMostPopular(search_term, api_token)
    song_list = listSongsFromArtistID(artist_id)
    for song in song_list:
        downloadSongFromURL(song['url'], download_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    download_list = "res/download.txt"
    api_token = "f-tXBsP-9KZM87bGN0YBlgWbobKvdCI0gVBYaGNLg04bsrJajFCkx-zLR-ayxfio"
    download_dir = "res/lyrics"
    getSongsFromWeb(download_list, api_token, download_dir)