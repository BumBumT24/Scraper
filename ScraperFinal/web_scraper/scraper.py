from flask import Flask, request, render_template, redirect, url_for
from bs4 import BeautifulSoup
import os
import urllib
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import asyncio
import re
import requests
from multiprocessing import Pool


username = urllib.parse.quote_plus('kacper')
password = urllib.parse.quote_plus('kacper')
mongo_url = f"mongodb+srv://{username}:{password}@baza1.1lctbku.mongodb.net/?retryWrites=true&w=majority&appName=Baza1"

client = MongoClient(mongo_url, server_api=ServerApi('1'))
mydb = client["scraped"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


async def naglowki(soup):
    headers = [header.text for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    return [str(header) for header in headers]


async def odnosniki(soup):
    links = [link.get('href') for link in soup.find_all('a')]
    return [str(link) for link in links]


async def adresy(soup):
    addresses = [address.text for address in soup.find_all('div', class_='adress-content')]
    return [str(address) for address in addresses]


async def email(soup):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_regex, soup.text)
    return list(set(emails))



async def scrape_and_store(url, db):
    print(f"Scraping data from {url}")
    response = requests.get(url)


    if response.status_code == 200:
        print("Successful response received (status 200)")
        soup = BeautifulSoup(response.text, 'html.parser')

        headers_task = naglowki(soup)
        links_task = odnosniki(soup)
        addresses_task = adresy(soup)
        emails_task = email(soup)

        headers, links, addresses, emails = await asyncio.gather(headers_task, links_task, addresses_task, emails_task)

        data = {
            'url': url if url else [],
            'headers': headers if headers else [],
            'links': links if links else [],
            'addresses': addresses if addresses else [],
            'emails': emails if emails else []
        }

        site_collection = mydb[url.replace("https://", "").replace("/", "_")]
        if headers:
            site_collection.insert_one({"type": "headers", "data": headers})

        if links:
            site_collection.insert_one({"type": "links", "data": links})

        if addresses:
            site_collection.insert_one({"type": "addresses", "data": addresses})

        if emails:
            site_collection.insert_one({"type": "emails", "data": emails})

        print("Inserting data into MongoDB")
        print("Data inserted into MongoDB")
        print("Data to insert:", data)
        return data
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')


def process_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Successful response received (status 200) for", url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headers = [header.text for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        links = [link.get('href') for link in soup.find_all('a')]
        addresses = [address.text for address in soup.find_all('div', class_='adress-content')]
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.text)
        return {
            'url': url,
            'headers': headers,
            'links': links,
            'addresses': addresses,
            'emails': list(set(emails))
        }
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code} for', url)
        return None


def scrape_default(db):
    urls = ['https://ans-elblag.pl', 'https://moodle.ans-elblag.pl', 'https://www.pkobp.pl/napisz-do-nas/',
            'https://pl.wikipedia.org/wiki/Cesarstwo_Rzymskie', 'https://www.python.org',
            'https://zsetczew.pl', 'http://sp8tczew.superszkolna.pl',
            'https://pzpn.pl', 'https://ug.edu.pl', 'https://github.com', 'https://www.kebabhubtczew.pl',
            'https://mcdonalds.pl','https://sp4tczew.bipszkola.pl/wiadomosci/832/wiadomosc/104678/statut_gimnazjum_nr_3_w_tczewie']

    scraped_data = []
    with Pool(processes=4) as pool:
        results = pool.map(process_url, urls)
        #Przetwarza wszystkie linki za pomoca czterech procesow
        pool.close()
        pool.join()
        pool.terminate()
    for data in results:
        if data is not None:
            site_collection = mydb[data['url'].replace("https://", "").replace("/", "_")]
            if data['headers']:
                site_collection.insert_one({"type": "headers", "data": data['headers']})
            if data['links']:
                site_collection.insert_one({"type": "links", "data": data['links']})
            if data['addresses']:
                site_collection.insert_one({"type": "addresses", "data": data['addresses']})
            if data['emails']:
                site_collection.insert_one({"type": "emails", "data": data['emails']})
            print("Inserting data into MongoDB for", data['url'])
            scraped_data.append(data)




    ##db['scraped_data'].insert_one(data)
    scraped=scraped_data
    return scraped


