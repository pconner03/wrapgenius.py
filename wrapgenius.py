import urllib2
import urllib
import json

from wrapgenius_secret import ACCESS_TOKEN

API_BASE = "http://api.genius.com/"

SEARCH_BASE = API_BASE+"search/?q="

ARTIST_BASE = API_BASE+"artists/"

URL_PARAM_ENCODER = urllib.quote_plus

RESPONSE_KEY = "response"

SEARCH_RESULTS_ARRAY_KEY = "hits"

ARTIST_KEY = "artist"

ARTIST_FORMAT = "?text_format=plain" #TODO - make customizable. Genius formats: plain, html, DOM

PLAINTEXT_DESCRIPTION_KEY = "plain"


def build_opener(access_token=ACCESS_TOKEN):
	opener = urllib2.build_opener()
	opener.addheaders = [("Authorization", "Bearer "+access_token)]
	return opener

class Genius:

	def __init__(self, opener=None):
		if not opener:
			opener = build_opener()
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
			searchResults.append(_searchResult(res["result"], self.opener)) # What is "highlights" sibling of "result"?
		return searchResults


class _searchResult:
	#static constants
	lyricsUpdated = "lyrics_updated_at"
	title = "title" 
	pyongsCount = "pyongs_count" 
	updatedByHumans = "updated_by_human_at"
	primaryArtist = "primary_artist"
	_id = "id"
	annotationCount = "annotation_count"
	url = "url"

	def __init__(self, data, opener=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		self.lyrics_updated_at = data[_searchResult.lyricsUpdated]
		self.title = data[_searchResult.title]
		self.pyongs_count = data[_searchResult.pyongsCount]
		self.updated_by_human_at = data[_searchResult.updatedByHumans]
		self.artist = _searchResultArtist(data[_searchResult.primaryArtist], self.opener)
		self.id = data[_searchResult._id]
		self.url = data[_searchResult.url]

		self.raw_data = data

	def __unicode__(self):
		return '"'+self.title+'" - '+self.url


	def getSong(self):
		return Song(self.id)

	def getArtist(self):
		return self.artist.getArtist()

class _searchResultArtist:
	imageUrl = "image_url"
	name = "name"
	_id = "id"
	url = "url"

	def __init__(self, data, opener=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		self.image_url = data[_searchResultArtist.imageUrl]
		self.name = data[_searchResultArtist.name]
		self.id = data[_searchResultArtist._id]
		self.url = data[_searchResultArtist.url]

	def __unicode__(self):
		return "<_searchResultArtist" + self.name +">"

	def getArtist(self):
		return Artist(self.id)


class Song:


	def __init__(self, _id, opener=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		# TODO


class Artist:

	description = "description"
	imageUrl = "image_url"
	name = "name"
	_id = "id"
	url = "url"

	def __init__(self, _id, opener=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		requestUrl = ARTIST_BASE + str(_id) + ARTIST_FORMAT

		data = json.loads(self.opener.open(requestUrl).read())[RESPONSE_KEY][ARTIST_KEY]

		self._build(data)
		

	def _build(self, data):
		# TODO -user stuff (new class)
		self.description = data[Artist.description][PLAINTEXT_DESCRIPTION_KEY]
		self.image_url = data[Artist.imageUrl]
		self.name = data[Artist.name]
		self.id = data[Artist._id]
		self.url = data[Artist.url]

		#What are tracking paths?


	def __unicode__(self):
		return self.name


g = Genius()
for r in g.search("Zion I"):
	print r.__unicode__()
	print r.getArtist().__unicode__()

