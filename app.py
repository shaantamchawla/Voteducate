from flask import Flask, render_template, request
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request, urllib.parse
import requests
import lxml
import json

app = Flask(__name__)

#obama search = https://www.google.com/webhp?oe=utf8&source=uds&start=0&h1=en&q=barack+obama

economic_key_words = ['economy', 'economic' 'tax', 'taxes', 'budget', 'debt', 'employment', 'recession', 'financial']
health_key_words = ['health care', 'obamacare', 'health reform', 'medicare', 'medicaid', 'health insurance', 'pandemic', 'condom', 'aids']
energy_key_words = ['energy', 'fracking', 'water quality', 'global warming', 'oil', 'nuclear', 'carbon', 'pollution', 'gas', 'coal', 
					'solar', 'electricity', 'recycling']
education_key_words = ['education', 'college', 'student loan', 'high school dropout', 'evolution', 'test score', 'teacher', 'pell']
crime_key_words = ['prison', 'incarceration' 'execution', 'death penalty', 'death sentence', 'capital punishment', 'drug deal', 'use drug', 
					'sell drug']
rights_key_words = ['civil rights', 'gay', 'lesbian', 'racial equality', 'black', 'affirmative action', 'job discrimination',
					'same-sex marriage', 'homosexuality', 'hate crime', 'racism', 'police brutality', 'police violence']
family_key_words = ['family', 'family values', 'religion', 'christianity', 'abstinence', 'childcare', 'child support', 'abortion', 
					'sexual abuse']
foreign_key_words = ['foreign policy', 'terrorism', 'world war', 'iraq', 'afghanistan', 'north korea', 'israel', 'iran', 'qaeda', 'taliban', 'isis',
					'foreign trade', 'export goods']
gun_key_words = ['gun control', 'gun rules', 'gun violence', '2nd amendment', 'second amendment', 'gun bans', 'semi-automatic', 
					'semi automatic']
security_key_words = ['homeland security', 'national security', 'nuclear weapons', 'nuclear stockpile', 'terrorist threats', 'privacy',
						'torture', 'ptsd', 'homeless veteran', 'drone', 'mass destruction']
immigration_key_words = ['immigration', 'illegal immigrant', 'border patrol', 'path to citizenship', ' legal immigrant', 'foreign student']
poverty_key_words = ['poverty', 'welfare', 'homelessness', 'inner city', 'minimum wage', 'food stamps', 'lower class']

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		search_query = request.form['query']
		facts_list = search(search_query)

		return render_template('summary.html', facts=facts_list)

	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

def search(search_query):
	name = search_query.split(" ")

	additions = ['views', 'political positions', 'political views' 'political beliefs']
	urls = []
	
	#try:
	#	for addition in additions:
	#		temp = search_query + " " + addition
	#		query = urllib.parse.urlencode({'q': (temp)})
	#		url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
	#		search_response = urllib.request.urlopen(url)
	#		search_results = search_response.read().decode("utf8")
	#		results = json.loads(search_results)
	#		data = results['responseData']
	#		hits = data['results']
	#		for hit in hits:
	#			if hit['url'] not in urls:
	#				urls.append(hit['url'])

	#except:

	url_extension = ""
	for part in name:
		if part != name[len(name) - 1]:
			url_extension += part + "_"
	url_extension += name[len(name) - 1] + ".htm"

	urls.append("http://www.ontheissues.org/" + url_extension)

	for url in urls:
		print(url + "\n")

	return analyze(urls)

def analyze(urls):
	facts = []

	for url in urls:
		#summarize the content on the page
		session = requests.Session()
		page = session.get(url)

		li = SoupStrainer('li')
		soup = BeautifulSoup(page.content, 'lxml', parse_only=li)

		info = str(soup.getText().encode('utf-8')).split('\\n')
		fact_count = 0

		for item in info:
			if fact_count > 20:
				break

			if item != "":
				for key_word in key_words:
					if key_word in item:
						temp = item
						if temp[-2:] == "\\r":
							temp = item[:-2]

						if temp[-1:] == ")":
							temp = temp[:-11]

						facts.append(temp)
						fact_count += 1
						break
	return facts

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)