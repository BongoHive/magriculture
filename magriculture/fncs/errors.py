class MagricultureException(Exception):
	"""
	All Exceptions in this project subclass this
	base exception
	"""

class ActorException(MagricultureException):
	"""
	Raised for exceptions relating to Actors
	"""

class CropReceiptException(MagricultureException):
	"""
	Raised when dealing with CropReceipts, typically
	when trying to sell something of which there isn't
	enough inventory
	"""
