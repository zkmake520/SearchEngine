from flask import Flask, render_template, redirect,url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField 
from wtforms.validators import DataRequired
from Indexer import Searcher
from LangProc import queryTerms
app = Flask(__name__)
Bootstrap(app)
searcher = Searcher("indexDB")
class SearchForm(Form):
    query = StringField("",validators=[DataRequired()])
    queryButton = SubmitField("Search")

@app.route("/",methods =["GET","POST"])
def index():
	searchForm = SearchForm(csrf_enabled =False)
	if searchForm.validate_on_submit():
		return redirect(url_for("search_results",query=searchForm.query.data))
	return  render_template("index.html",form=searchForm)

@app.route("/search_results/<query>")
def search_results(query):
	queryStr = queryTerms(query)
	queryStr = [term for term in queryStr if term != ""]
	docId = searcher.findDocument_AND(queryStr)
	urls = [searcher.getUrl(id) for id in docId]
	snippets = [searcher.getSnippets(queryStr,id) for id in docId]
	urlsAndSnippets= zip(urls,snippets)
	return render_template("search_results.html",query = query ,urlsAndSnippets= urlsAndSnippets)
if __name__ == "__main__":
    app.run(debug=True)