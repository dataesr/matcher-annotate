import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

from flask import render_template
from . import app

DATA_FOLDER = 'data'
DATA_URL = 'https://storage.gra.cloud.ovh.net/v1/AUTH_32c5d10cb0fe4519b957064a111717e3/models/pubmed_and_h2020_affiliations.json'
MATCHER_TYPE = 'grid'
MATCHER_URL = 'http://localhost:5004'

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


@app.route('/logs')
def logs():
    with open(f'{DATA_FOLDER}/matcher-affiliation-grids.jsonl') as file:
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


@app.route('/matcher_check_strategies')
def matcher_check_strategies():
    # Load data
    data = requests.get(DATA_URL).json()
    df = pd.DataFrame(data).rename(columns={'grid': 'grid_expected'})
    # Remove data with no grid
    df = df[df.grid_expected.map(len) > 0]
    df = df[df['source'] == 'pubmed']
    df['grid_matched'] = None
    df['strategy'] = None
    df['is_matched'] = 'empty'
    for index, row in df.iterrows():
        query = row.label
        grid_expected = row.grid_expected
        if len(grid_expected) > 0:
            for strategy in strategies:
                strategy = [[strategy]]
                json_object = {'type': MATCHER_TYPE, 'query': query, 'strategies': strategy}
                response = requests.post(url=f'{MATCHER_URL}/match_api', json=json_object)
                grid_matched = response.json().get('results')
                if len(grid_matched) > 0:
                    # Stop at the first result found
                    break
            # If at least one strategy has a match
            if len(grid_matched) > 0:
                df['grid_matched'][index] = grid_matched
                df['strategy'][index] = strategy[0][0]
                diff = list(set(grid_expected) - set(grid_matched))
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
            print(f'No grid expected for query {query}')
    # Calculate the precision by strategy
    df_results = df
    print(len(df_results))
    df_pubmed_filtered = df_results[df_results.strategy.notnull()]
    print(len(df_pubmed_filtered))
    print('---')
    results = {}
    logs = []
    for index, row in df_pubmed_filtered.iterrows():
        strategy = ','.join(row.get('strategy'))
        if strategy not in results.keys():
            results[strategy] = {'vp': 0, 'fp': 0, 'count': 0}
        results[strategy]['count'] += 1
        grids_matched = row.get('grid_matched', [])
        grids_matched = grids_matched if grids_matched else []
        for grid in grids_matched:
            grid_expected = row.get('grid_expected', [])
            if grid in grid_expected:
                results[strategy]['vp'] += 1
            else:
                results[strategy]['fp'] += 1
                if strategy == 'grid_name,grid_city,grid_country':
                    logs.append({'query': row.get('label'), 'strategy': strategy, 'grid_expected': ','.join(grid_expected), 'grid_matched': grid})
    for result in results:
        results[result]['precision'] = round(results[result]['vp'] / (results[result]['vp'] + results[result]['fp']) * 100, 2)
    with open(f'{DATA_FOLDER}/matcher-affiliation-examples.jsonl', 'w') as file:
        for log in logs:
            json.dump(log, file)
            file.write('\n')
    return results
