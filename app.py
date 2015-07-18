from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import urllib.request, urllib.parse
import json

app = Flask(__name__)

#obama search = https://www.google.com/webhp?oe=utf8&source=uds&start=0&h1=en&q=barack+obama

key_words = ['tax', 'taxes', 'gay', 'lesbian', 'employment', 'union', 'abortion', 'discrimination', 'affirmative action', 
	'privacy', 'gambling', 'torture', 'immigration', 'education', 'teachers', 'energy', 'gas', 'nuclear', 'renewable', 
	'global warning', 'loans', 'student loans', 'welfare', 'social security', 'food stamps', 'disability', 'hate crime', 'police abuse', 
	'police brutality', 'prison', 'crime', 'execution', 'death penalty', 'death sentence', 'capital punishment', 'gun', 'weapon',
	'drone', 'combat', 'mass destruction', 'chemical', 'biological', 'science' 'terror', 'war', 'drugs', 'marijuana', 
	'medical marijuana', 'capitalism', 'economy', 'policy', 'legislation', 'law', 'view', 'opinion', 'security', 'minimum wage', 'god', 
	'evolution', 'israel', 'iraq', 'afghanistan', 'north korea', 'mexico', 'cuba', 'iran', 'pakistan', 'taliban', 'al-qaeda', 'palestine', 
	'gaza', 'oil', 'shooting', 'environment', 'healthcare', 'pension', 'poverty', 'middle class', 'lower class', 'upper class', 'college',
	'school', 'transportation', 'fracking', 'water quality', 'foreign', 'isis', 'insurance', 'carbon', 'greenhouse', 'pandemic',
	'epidemic', 'housing', 'racism', 'racial', 'race', 'black', 'african american', 'foreign', 'foreign policy', 'foreign relations']

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		query = request.form['query']

	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

def search(search_query):
	name = search_query.split(" ")
	first_name = name[0]

	if len(name) > 1:
		last_name = name[len(name) - 1]

	additions = ['views', 'political positions', 'political views' 'political beliefs']
	urls = []
	
	for addition in additions:
		temp = search_query + " " + addition
		query = urllib.parse.urlencode({'q': (temp)})
		url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
		search_response = urllib.request.urlopen(url)
		search_results = search_response.read().decode("utf8")
		results = json.loads(search_results)
		data = results['responseData']
		hits = data['results']
		for hit in hits:
			if hit['url'] not in urls:
				urls.append(hit['url'])

	for url in urls:
		print(url + "\n")

	analyze(urls)

	#if on_issues_count == 0:
	#	urls.append("http://www.ontheissues.org/" + first_name + "_" + last_name + ".htm")

def analyze(urls):
	facts = []

	for url in urls:
		#summarize the content on the page
		page = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(page, "html.parser")
		info = str(soup.getText().encode('UTF-8')).split('\\n')
		for item in info:
			if item != "":
				for key_word in key_words:
					if key_word in item:
						facts.append(item)
						break

		for fact in facts:
			print(fact)

#analyze(['https://en.wikipedia.org/wiki/Political_positions_of_Barack_Obama'])

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)