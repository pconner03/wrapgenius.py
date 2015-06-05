import urllib2
import urllib
import json

from wrapgenius_secret import ACCESS_TOKEN

API_BASE = "http://api.genius.com/"

SEARCH_BASE = API_BASE+"search/?q="

URL_PARAM_ENCODER = urllib.quote_plus

RESPONSE_KEY = "response"

SEARCH_RESULTS_ARRAY_KEY = "hits"


class Genius:

	def __init__(self, access_token=ACCESS_TOKEN):
		self.access_token = access_token
		opener = urllib2.build_opener()
		opener.addheaders = [("Authorization", "Bearer "+self.access_token)]
		self.opener = opener
		

	def search(self, searchTerm):
		'''
		search songs
		'''
		searchUrl = SEARCH_BASE+URL_PARAM_ENCODER(searchTerm)
		# TODO - exception handling
		requestResults = json.loads(self.opener.open(searchUrl).read())[RESPONSE_KEY][SEARCH_RESULTS_ARRAY_KEY]
		searchResults = []
		for res in requestResults:
			searchResults.append(res) # TODO - make artist and song classes 
		return searchResults



class Song:
	def __init__(self, dictionary): #is this the best way to do this? Maybe pass url instead, but that would be slower (new request for every search result)
		pass
		# TODO


class Artist:
	def __init__(self, dictionary):
		pass
		# TODO


g = Genius()
print g.search("Zion I")

