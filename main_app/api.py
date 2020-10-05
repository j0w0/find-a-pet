import os
import requests

PETFINDER_CLIENT_ID = os.getenv("PETFINDER_CLIENT_ID")
PETFINDER_CLIENT_SECRET = os.getenv("PETFINDER_CLIENT_SECRET")

BASE_URL = 'https://api.petfinder.com/v2/'


def get_animals():
    endpoint = BASE_URL + 'animals'
    return base_request(endpoint)


def get_animal(animal_id):
    endpoint = BASE_URL + f'animals/{animal_id}'
    return base_request(endpoint)


def get_animal_types():
    endpoint = BASE_URL + 'types'
    return base_request(endpoint)


def get_animals_type(animal_type):
    endpoint = BASE_URL + f'types/{animal_type}'
    return base_request(endpoint)


def get_animal_breed(animal_type):
    endpoint = BASE_URL + f'types/{animal_type}/breeds'
    return base_request(endpoint)


def filter_animals(query_string):
    endpoint = BASE_URL + f'animals{query_string}'
    return base_request(endpoint)


def base_request(endpoint):
    data = {}
    headers = {'Authorization': 'Bearer ' + get_access_token()}
    response = requests.request('GET', endpoint, headers=headers, data=data)
    return response.json()


def get_access_token():
    endpoint = BASE_URL + 'oauth2/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': PETFINDER_CLIENT_ID,
        'client_secret': PETFINDER_CLIENT_SECRET
    }
    response = requests.post(endpoint, data=data)
    return response.json()['access_token']
