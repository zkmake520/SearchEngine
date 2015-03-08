from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import sent_tokenize, TreebankWordTokenizer
import itertools
import string

def reduce(text):
	sents = sent_tokenize(text)
	tokens = list(itertools.chain(*[TreebankWordTokenizer().tokenize(sent) for sent in sents]))
	stems = [PorterStemmer().stem(token) for token in tokens]
	terms =[stem.lower() for stem in stems if stem not in string.punctuation]
	return terms

def queryTerms(query):
	return reduce(query)

def docTerms(doc):
	return reduce(doc)