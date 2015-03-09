from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import sent_tokenize, TreebankWordTokenizer
import itertools
import string
class Term():     # by define this, then what we store and query is the instance of Term. thus compare should be Term.stem not instance
	def __init__(self,originalWord):   #since we need to show the original word so it's a good idea to put stem and word teogether
		self.originalWord = originalWord
		self.stem = PorterStemmer().stem(originalWord).lower()
	def __eq__(self,other):
		return self.stem == other.stem
	def __hash__(self):
		return hash(self.stem)
def tokenizeText(text):
	sents = sent_tokenize(text)
	tokens = list(itertools.chain(*[TreebankWordTokenizer().tokenize(sent) for sent in sents]))
	stems = [Term(token) for token in tokens]
	return stems

def queryTerms(query):
	return tokenizeText(query)

def docTerms(doc):
	return tokenizeText(doc)