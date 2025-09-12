import requests
from os import environ

CHALLENGE_HOST = environ["CHALLENGE_HOST"] # in production, CHALLENGE_HOST="sideralnoise.404ctf.fr"
SATELLITE_TOKEN = environ["SATELLITE_TOKEN"]

def fetch_noise(noise_id):
    # fetch noise from the satellite
    s = requests.Session()
    s.cookies.set('token', SATELLITE_TOKEN, domain=CHALLENGE_HOST)
    response = s.get(f'http://{CHALLENGE_HOST}/satellite/noise/{noise_id}')
    return response.text