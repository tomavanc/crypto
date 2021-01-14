from flask import Flask
from threading import Thread

from util import getEnvKey

app = Flask('')

@app.route('/')
def home():
  return 'Crypto is live'

def run():
  app.run(host=getEnvKey('GUILD'),port=getEnvKey('PORT'))

def keep_alive():
  t = Thread(target=run)
  t.start()