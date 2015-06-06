import urllib2
import urllib
import json

from wrapgenius_secret import ACCESS_TOKEN

API_BASE = "http://api.genius.com/"

SEARCH_BASE = API_BASE+"search/?q="

ARTIST_BASE = API_BASE+"artists/"

SONG_BASE = API_BASE+"songs/"

URL_PARAM_ENCODER = urllib.quote_plus

RESPONSE_KEY = "response"

SEARCH_RESULTS_ARRAY_KEY = "hits"

ARTIST_KEY = "artist"

SONG_KEY = "song"

TEXT_FORMAT = "?text_format=plain" #TODO - make customizable. Genius formats: plain, html, DOM

PLAINTEXT_DESCRIPTION_KEY = "plain"


def build_opener(access_token=ACCESS_TOKEN):
	opener = urllib2.build_opener()
	opener.addheaders = [("Authorization", "Bearer "+access_token)]
	opener.addheaders = [("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)")] #Default user agent doesn't return "lyrics" field in /songs/{id}
	# Lyrics are returned in browser and with curl, though. 

	
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
		artistData = data[_searchResult.primaryArtist]

		self.artist_name = artistData[Artist.name]
		self.artist = Artist(data=artistData, opener=self.opener)
		self.id = data[_searchResult._id]
		self.url = data[_searchResult.url]

		self.raw_data = data

	def __unicode__(self):
		return '"'+self.title+'" - '+self.url


	def getSong(self):
		# Not using song class in search result because there's a lot missing here
		# Good idea or not? Could have lyrics/additional metadata requested separately, 
		# because song name and artist are available already
		return Song(_id=self.id, opener=self.opener)

	def getArtist(self):
		return self.artist


class Song:

	producers = "producer_artists"
	stats = "stats"
	lyricsUpdated = "lyrics_updated_at"
	description = "description"
	featuredArtists = "featured_artists"
	writers = "writer_artists"
	lyrics = "lyrics"
	title = "title"
	_id = "id"
	url = "url"
	primaryArtist = "primary_artist"

	def __init__(self, _id, opener=None, primary_artist=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		self.primary_artist = primary_artist #Avoid redundant request if we already got a full artist (e.g. created song object from artist.getSongs)
		self._build(_id)

	def _build(self, _id):
		requestUrl = SONG_BASE + str(_id) + TEXT_FORMAT
		data = json.loads(self.opener.open(requestUrl).read())[RESPONSE_KEY][SONG_KEY]
		self._buildFromData(data)

	def _buildFromData(self, data):
		# TODO - verified annotations by

		self.producer_artists = [Artist(data=d, opener=self.opener) for d in data[Song.producers]]
		
		self.stats = data[Song.stats]
		self.lyrics_updated_at = data[Song.lyricsUpdated]

		self.description = data[Song.description][PLAINTEXT_DESCRIPTION_KEY]	

		self.featured_artists = [Artist(data=d, opener=self.opener) for d in data[Song.featuredArtists]]

		self.writer_artists = [Artist(data=d, opener=self.opener) for d in data[Song.writers]]

		self.lyrics = data[Song.lyrics][PLAINTEXT_DESCRIPTION_KEY]

		self.title = data[Song.title]

		self.id = data[Song._id]

		self.url = data[Song.url]

		if not self.primary_artist:
			self.primary_artist = Artist(data=data[Song.primaryArtist], opener=self.opener)
		# TODO - media (e.g. youtube link), api/tracking paths??, user stuff, 
		# everything with annotations (both lyrics and description)
		
class Artist:

	description = "description"
	imageUrl = "image_url"
	name = "name"
	_id = "id"
	url = "url"

	# TODO - get songs

	def __init__(self, _id=None, data=None, opener=None):
		if not opener:
			opener = build_opener()
		self.opener = opener

		if data:
			self._buildFromData(data)
		else:
			data = self._getData()
			requestUrl = ARTIST_BASE + str(_id) + TEXT_FORMAT
			requestData = json.loads(self.opener.open(requestUrl).read())[RESPONSE_KEY][ARTIST_KEY]
			self._buildFromData(data)
		

	def _buildFromData(self, data):
		# TODO -user stuff (new class)
		# Won't be present in song or result artist object (Like description)
		if Artist.description in data:
			self.description = data[Artist.description][PLAINTEXT_DESCRIPTION_KEY]
			self.descriptionAvailable = True
		else:
			self.descriptionAvailable = False
			self.description = None

		self.image_url = data[Artist.imageUrl]
		self.name = data[Artist.name]
		self.id = data[Artist._id]
		self.url = data[Artist.url]

		#What are tracking paths?

	def _getData(self):
		requestUrl = ARTIST_BASE + str(self.id) + TEXT_FORMAT
		requestData = json.loads(self.opener.open(requestUrl).read())[RESPONSE_KEY][ARTIST_KEY]
		return requestData


	def getDescription(self):
		#blocking if unavailable
		if not self.descriptionAvailable:
			data = self._getData()
			self.description = data[Artist.description][PLAINTEXT_DESCRIPTION_KEY]
			self.descriptionAvailable = True

		return self.description

	def __unicode__(self):
		return self.name

if __name__ == "__main__":
	g = Genius()
	res = g.search("Outkast")
	print res[0].getArtist().getDescription()
	for r in res:
		print r.title +":"
		print r.getSong().lyrics
		print "\n\n"
		# print r.artist.__unicode__()

