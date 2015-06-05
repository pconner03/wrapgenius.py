import urllib2


from wrapgenius_secret.py import ACCESS_TOKEN

class Genius:

	def __init__(Self, access_token=ACCESS_TOKEN):
		self.access_token = access_token
		opener = urllib2.build_opener()
		

	def search(self, searchTerm):


