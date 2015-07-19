from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request, urllib.parse
import requests
import sendgrid
import lxml
import json

app = Flask(__name__)

#obama search = https://www.google.com/webhp?oe=utf8&source=uds&start=0&h1=en&q=barack+obama

economic_key_words = ['economy', 'economic' 'tax', 'taxes', 'budget', 'debt', 'employment', 'recession', 'financial']
health_key_words = ['health', 'obamacare', 'health', 'medicare', 'medicaid', 'health insurance', 'pandemic', 'condom', 'aids']
energy_key_words = ['energy', 'fracking', 'water quality', 'global warming', 'oil', 'nuclear', 'carbon', 'pollution', 'gas', 'coal', 
					'solar', 'electricity', 'recycling', 'green energy', 'renewable energy', 'greenhouse gas']
education_key_words = ['education', 'college', 'student loan', 'high school dropout', 'evolution', 'test score', 'teacher', 'pell']
crime_key_words = ['prison', 'incarceration' 'execution', 'death penalty', 'death sentence', 'capital punishment', 'drug deal', 'use drug', 
					'sell drug']
rights_key_words = ['civil rights', 'gay', 'lesbian', 'racial equality', 'black', 'affirmative action', 'job discrimination',
					'same-sex marriage', 'homosexuality', 'hate crime', 'racism', 'police brutality', 'police violence']
family_key_words = ['family', 'childhood', 'family values', 'religion', 'christianity', 'abstinence', 'childcare', 'child support', 'abortion', 
					'sexual abuse']
foreign_key_words = ['foreign policy', 'terrorism', 'world war', 'iraq', 'afghanistan', 'north korea', 'israel', 'iran', 'qaeda', 'taliban', 'isis',
					'foreign trade', 'export goods']
gun_key_words = ['gun control', 'gun rules', 'gun violence', '2nd amendment', 'second amendment', 'gun bans', 'semi-automatic', 
					'semi automatic', 'gun background']
security_key_words = ['homeland security', 'national security', 'nuclear weapons', 'nuclear stockpile', 'terrorist threats', 'privacy',
						'torture', 'ptsd', 'homeless veteran', 'drone', 'mass destruction']
immigration_key_words = ['immigration', 'illegal immigrant', 'border patrol', 'path to citizenship', ' legal immigrant', 'foreign student']
poverty_key_words = ['poverty', 'welfare', 'homelessness', 'inner city', 'minimum wage', 'food stamps', 'lower class']

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		search_query = request.form['query']
		election = request.form['election']
		facts_list = search(search_query, election)
		name = search_query.title()

		emailMsg = ""

		for category in facts_list:
			for fact in category:
				emailMsg += fact[4:] + "\n"
			emailMsg += "\n"

		print(emailMsg)

		#get pic from wikipedia page
		session = requests.Session()
		page = session.get('https://en.wikipedia.org/wiki/' + get_url_extension(name.split(" "), ""))

		tree = BeautifulSoup(page.content, 'lxml')
		img_link = tree.find_all('img')[3].get('src')

		return render_template('summary.html', facts=facts_list, name=name, img_link=img_link, emailMsg=emailMsg)
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/summary', methods=['GET', 'POST'])
def summary():
	if request.method == 'POST':
		recipient = request.form['recipient']
		print(recipient)
		origBody = request.form['emailMsg']
		body = ""
		for i in range(len(origBody) - 3):
			if origBody[i] != '[' and origBody[i] != ']' and origBody[i] != "\\" and origBody[i] != ",":
				body += origBody[i]
				if origBody[i] == "\'" and origBody[i + 1] != "s":
					body += "\n"


		sg = sendgrid.SendGridClient('shaantamc', 'Coolab9')
		message = sendgrid.Mail()
		message.add_to(recipient)
		message.set_subject('Your Voteducate Candidate Report')
		message.set_text(body)
		message.set_from('Voteducate')
		status, msg = sg.send(message)
		print(status, msg)

	return render_template('sent.html')

def search(search_query, election):
	name = search_query.split(" ")

	additions = ['views', 'political positions', 'political views' 'political beliefs']
	urls = []

	urls.append("http://www.ontheissues.org/" + get_url_extension(name, election) + ".htm")

	for url in urls:
		print(url + "\n")

	return analyze(urls)

def google_search_results(search_query):
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

def get_url_extension(name, election):
	url_extension = ""
	if election == 'senate':
		url_extension += "Senate/"
	for part in name:
		if part != name[len(name) - 1]:
			url_extension += part + "_"
	url_extension += name[len(name) - 1]

	return url_extension

def analyze(urls):
	economic_facts = []
	health_facts = []
	energy_facts = []
	education_facts = []
	crime_facts = []
	rights_facts = []
	family_facts = []
	foreign_facts = []
	gun_facts = []
	security_facts = []
	immigration_facts = []
	poverty_facts = []
	facts = []

	for url in urls:
		#summarize the content on the page
		session = requests.Session()
		page = session.get(url)

		li = SoupStrainer('li')
		soup = BeautifulSoup(page.content, 'lxml', parse_only=li)

		info = str(soup.getText().encode('ascii', 'ignore')).split('\\n')
		fact_count = 0

		for line in info:
			found_flag = False
			if fact_count > 500:
				break

			if line != "" and '?' not in line and 'OpEd' not in line:
				if found_flag == False:
					for key_word in economic_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							economic_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in health_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							health_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in energy_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							energy_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in education_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							education_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in crime_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							crime_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in rights_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							rights_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in family_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							if "b\'" in temp:
								temp = temp[2:]

							family_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in foreign_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							foreign_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in gun_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							gun_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in security_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							security_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in immigration_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							immigration_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

				if found_flag == False:
					for key_word in poverty_key_words:
						if key_word in line:
							temp = line
							if temp[-2:] == "\\r":
								temp = line[:-2]

							if temp[-1:] == ")":
								temp = temp[:-11]

							if "FactCheck" in temp:
								temp = temp[15:]

							poverty_facts.append(temp)
							found_flag = True
							fact_count += 1

							#break out of inner loop, go on to next line
							break

	facts.extend((economic_facts, health_facts, energy_facts, education_facts, crime_facts, rights_facts, family_facts, foreign_facts, 
		gun_facts, security_facts, immigration_facts, poverty_facts))

	return facts

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)