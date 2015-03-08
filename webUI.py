from flask import Flask, render_template, redirect,url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField 
from wtforms.validators import DataRequired
from Indexer import Searcher
app = Flask(__name__)
Bootstrap(app)
searcher = Searcher("indexDB")
class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])
    queryButton = SubmitField("Search")

@app.route("/",methods =["GET","POST"])
def index():
	searchForm = SearchForm(csrf_enabled =False)
	if searchForm.validate_on_submit():
		return redirect(url_for("search_results",query=searchForm.query.data))
	return  render_template("index.html",form=searchForm)

@app.route("/search_results/<query>")
def search_results(query):
	queryStr = query.split(" ")
	queryStr = [word for word in queryStr if word != ""]
	docId = searcher.findDocument_AND(queryStr)
	urls = [searcher.getUrl(id) for id in docId]
	snippets = [searcher.getSnippets(queryStr,id) for id in docId]
	urlsAndSnippets= zip(urls,snippets)
	print urlsAndSnippets
	return render_template("search_results.html",query = query ,urlsAndSnippets= urlsAndSnippets)
if __name__ == "__main__":
    app.run(debug=True)