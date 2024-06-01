from flask import Flask, render_template, request,url_for,redirect
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import urllib
from web_scraper.scraper import scrape_and_store,scrape_default
import asyncio
from requests.exceptions import MissingSchema
from multiprocessing import pool


app = Flask(__name__)

username = urllib.parse.quote_plus('kacper')
password = urllib.parse.quote_plus('kacper')
mongo_url = f"mongodb+srv://{username}:{password}@baza1.1lctbku.mongodb.net/?retryWrites=true&w=majority&appName=Baza1"

client = MongoClient(mongo_url, server_api=ServerApi('1'))
mydb = client["scraped"]

def serialize_document(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc




@app.route('/default_data',methods=['GET'])
def default_data():
    if request.method == 'GET':
        dataR = scrape_default(mydb)  # Pobranie danych za pomocą funkcji scrape_random
        return render_template('default_data.html', dataR=dataR)


@app.route('/delete_default_all', methods=['POST'])
def delete_default_all():
    if request.method == 'POST':
        # Lista adresów URL, dla których chcemy usunąć dane
        urls = ['https://ans-elblag.pl', 'https://moodle.ans-elblag.pl', 'https://www.pkobp.pl/napisz-do-nas/',
                'https://pl.wikipedia.org/wiki/Cesarstwo_Rzymskie', 'https://www.python.org',
                'https://zsetczew.pl', 'http://sp8tczew.superszkolna.pl',
                'https://pzpn.pl', 'https://ug.edu.pl', 'https://github.com', 'https://www.kebabhubtczew.pl',
                'https://mcdonalds.pl', 'https://sp4tczew.bipszkola.pl/wiadomosci/832/wiadomosc/104678/statut_gimnazjum_nr_3_w_tczewie']

        # Usuwanie danych dla każdego adresu URL na liście
        for url in urls:
            collection_name = url.replace("https://", "").replace("/", "_")
            print("Deleting data for URL:", url)
            mydb[collection_name].drop()

        # Opcjonalnie, usuń wszystkie wpisy z default_collections po usunięciu kolekcji
        mydb["default_collections"].delete_many({"collections": {"$in": urls}})

        return redirect(url_for('index'))



@app.route('/delete_default_data', methods=['POST'])
def delete_default_data():
    if request.method == 'POST':
        urls_to_delete = request.form.getlist('url_to_delete')
        print("URLs to delete:", urls_to_delete)  # Sprawdzenie, czy poprawnie pobierane są adresy URL
        for url in urls_to_delete:
            collection_name = url.replace("https://", "").replace("/", "_")
            print("Deleting data for URL:", url)  # Sprawdzenie, czy poprawnie wybierane są adresy URL do usunięcia
            mydb[collection_name].drop()
        return redirect(url_for('index'))


@app.route('/delete_chosen_data', methods=['POST'])
def delete_chosen_data():
    if request.method == 'POST':
        urls_to_delete = request.form.getlist('url_to_delete')
        print("URLs to delete:", urls_to_delete)  # Sprawdzenie, czy poprawnie pobierane są adresy URL
        for url in urls_to_delete:
            collection_name = url.replace("https://", "").replace("/", "_")
            print("Deleting data for URL:", url)  # Sprawdzenie, czy poprawnie wybierane są adresy URL do usunięcia
            mydb[collection_name].drop()
        return redirect(url_for('all_data'))

@app.route('/all_data')
def all_data():
    collections = mydb.list_collection_names()
    all_data = {}
    for collection_name in collections:
        collection = mydb[collection_name]
        documents = collection.find()
        all_data[collection_name] = [serialize_document(doc) for doc in documents]

    return render_template('all_data.html', all_data=all_data)

@app.route('/delete_all', methods=['POST'])
def delete_all():
    collections = mydb.list_collection_names()
    for collection_name in collections:
        mydb[collection_name].drop()  # Drop the collection
    return redirect(url_for('all_data'))




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Scraping started")
        url = request.form['url']
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:

            data = loop.run_until_complete(scrape_and_store(url, mydb))
            print("Scraping finished")
            if data:
                return render_template('scraped.html', data=data)
            else:
                return render_template('Failed_to_retrieve_data.html')
        except MissingSchema:
            return render_template('invalid_url.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=int("5000"), host='0.0.0.0')