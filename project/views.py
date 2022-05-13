from bs4 import BeautifulSoup
import json
import pandas as pd
import requests

from flask import jsonify, render_template, request
from . import app
from .config import DATA_URL, LOG_FILE_PATH, MATCHER_URL


strategies = [
    ['grid_name', 'grid_acronym', 'grid_city', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_city', 'grid_country_code'],
    ['grid_name', 'grid_city', 'grid_country'],
    ['grid_name', 'grid_city', 'grid_country_code'],
    ['grid_acronym', 'grid_city', 'grid_country'],
    ['grid_acronym', 'grid_city', 'grid_country_code'],
    ['grid_name', 'grid_acronym', 'grid_city'],
    ['grid_name', 'grid_acronym', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_country_code'],
    ['grid_name', 'grid_city'],
    ['grid_name', 'grid_acronym', 'grid_region', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_region', 'grid_country_code'],
    ['grid_name', 'grid_region', 'grid_country'],
    ['grid_name', 'grid_region', 'grid_country_code'],
    ['grid_acronym', 'grid_region', 'grid_country'],
    ['grid_acronym', 'grid_region', 'grid_country_code'],
    ['grid_name', 'grid_acronym', 'grid_region'],
    ['grid_name', 'grid_acronym', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_country_code'],
    ['grid_name', 'grid_region'],
    ['grid_name', 'grid_acronym', 'grid_cities_by_region', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_cities_by_region', 'grid_country_code'],
    ['grid_name', 'grid_cities_by_region', 'grid_country'],
    ['grid_name', 'grid_cities_by_region', 'grid_country_code'],
    ['grid_acronym', 'grid_cities_by_region', 'grid_country'],
    ['grid_acronym', 'grid_cities_by_region', 'grid_country_code'],
    ['grid_name', 'grid_acronym', 'grid_cities_by_region'],
    ['grid_name', 'grid_acronym', 'grid_country'],
    ['grid_name', 'grid_acronym', 'grid_country_code'],
    ['grid_name', 'grid_cities_by_region']
]


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/annotate')
def navigate():
    return render_template('annotate.html')


@app.route('/logs')
def logs():
    with open(LOG_FILE_PATH) as file:
        logs = file.readlines()
    return {'logs': logs}


@app.route('/grid/<id>')
def grid(id):
    url = f'https://grid.ac/institutes/{id}'
    results = requests.get(url=url).text
    html = BeautifulSoup(results, 'lxml')
    name = html.find_all('h1')[0].text
    other_names = [t.text.strip() for t in html.find_all('li', {'itemprop': 'alternateName'})]
    other_names += [t.text.strip() for t in html.find_all('span', {'itemprop': 'alternateName'})]
    city = html.find_all('table', {'class': 'table fon'})[0].find_all('td', text='City')[0].parent.find_all('td')[1].text
    region = html.find_all('table', {'class': 'table fon'})[0].find_all('td', text='Admin 1 Region')[0].parent.find_all('td')[1].text
    country = html.find_all('table', {'class': 'table fon'})[0].find_all('td', text='Country/Territory')[0].parent.find_all('td')[1].text
    return {
        'id': id,
        'name': name,
        'other_names': other_names,
        'city': city,
        'region': region,
        'country': country,
        'url': url
    }


@app.route('/rnsr/<id>')
def rnsr(id):
    url = f'http://185.161.45.213/organizations/organizations/{id}'
    headers = {'Authorization': 'Basic cm9vdDp0b25uZXJyZTJCcmVzdA=='}
    results = requests.get(url=url, headers=headers).json()
    name = results.get('names')[0].get('name_fr')
    acronym = results.get('names')[0].get('acronym_fr')
    address = results.get('addresses')[0]
    city = address.get('city')
    country = address.get('country')
    code_number = results.get('code_numbers')[0]
    supervisor = results.get('supervisors')[0].get('name')
    return {
        'id': id,
        'name': name,
        'acronym': acronym,
        'city': city,
        'country': country,
        'code_number': code_number,
        'supervisor': supervisor,
        'url': url
    }


@app.route('/check')
def check():
    # Load data
    type = request.args.get('type', 'grid')
    data = requests.get(DATA_URL).json()
    df = pd.DataFrame(data).rename(columns={'grid': 'expected'})
    # Remove data with no expectation
    df = df[df.expected.map(len) > 0]
    df = df[df['source'] == 'pubmed']
    df['matched'] = None
    df['strategy'] = None
    df['is_matched'] = 'empty'
    # df = df[:50]
    for index, row in df.iterrows():
        query = row.label
        expected = row.expected
        if len(expected) > 0:
            for strategy in strategies:
                strategy = [[strategy]]
                json_object = {'type': type, 'query': query, 'strategies': strategy}
                response = requests.post(url=f'{MATCHER_URL}/match_api', json=json_object)
                matched = response.json().get('results')
                if len(matched) > 0:
                    # Stop at the first result found
                    break
            # If at least one strategy has a match
            if len(matched) > 0:
                df['matched'][index] = matched
                df['strategy'][index] = strategy[0][0]
                diff = list(set(expected) - set(matched))
                if len(diff) == 0:
                    is_matched = 'complete'
                elif len(diff) > 0:
                    is_matched = 'missing values'
                elif len(diff) < 0:
                    is_matched = 'too many values'
                else:
                    is_matched = 'error'
                df['is_matched'][index] = is_matched
        else:
            # This should never happen anymore
            print(f'Nothing expected for query {query}')
    # Calculate the precision by strategy
    df_results = df
    df_pubmed_filtered = df_results[df_results.strategy.notnull()]
    results = {}
    logs = []
    for index, row in df_pubmed_filtered.iterrows():
        strategy = ','.join(row.get('strategy'))
        if strategy not in results.keys():
            results[strategy] = {'vp': 0, 'fp': 0, 'count': 0}
        results[strategy]['count'] += 1
        matcheds = row.get('matched', [])
        matcheds = matcheds if matcheds else []
        for matched in matcheds:
            expected = row.get('expected', [])
            if matched in expected:
                results[strategy]['vp'] += 1
            else:
                results[strategy]['fp'] += 1
                # Log only FP results
                logs.append({'type': type, 'query': row.get('label'), 'strategy': strategy, 'expected': ','.join(expected), 'matched': matched})
    for result in results:
        results[result]['precision'] = round(results[result]['vp'] / (results[result]['vp'] + results[result]['fp']) * 100, 2)
    with open(LOG_FILE_PATH, 'w') as file:
        for log in logs:
            json.dump(log, file)
            file.write('\n')
    with open('data/results.json', 'w') as file:
        json.dump(results, file)
    return jsonify({'status': 'success'})
