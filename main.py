import discord
import requests
import json

import random
import string

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from server import keep_alive
from util import getEnvKey

client = discord.Client()

@client.event
async def on_connect(self):
  print('Connecting to discord!')

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

  await job()

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('$hello'):
    random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    await message.channel.send(random_text)

  if msg.startswith('$search'):
    await message.channel.send(get_coin_quote(msg.split()[1]))

async def job():
  channel = discord.utils.get(client.get_all_channels(), guild__name=getEnvKey('GUILD'), name=getEnvKey('CHANNEL'))

  await channel.send("**CRYPTO'S DAILY UPDATE**")
  await send_coin_update(channel)
  
async def send_coin_update(channel):
  btc = get_coin_quote('btc')
  bch = get_coin_quote('bch')
  link = get_coin_quote('link')
  ltc = get_coin_quote('ltc')
  eth = get_coin_quote('eth')

  await channel.send(btc)
  await channel.send(bch)
  await channel.send(link)
  await channel.send(ltc)
  await channel.send(eth)

def get_coin_quote(coin_symbol):
  coin_key = getEnvKey('COINAPI')
  params = {'CMC_PRO_API_KEY': coin_key, 'convert': 'EUR', 'symbol': coin_symbol }

  response = requests.get(getEnvKey('COINMARKETCAP'), params=params)
  
  json_data = json.loads(response.text)

  if json_data['status']['error_code'] > 200:
    print(json_data['status']['error_message'])
    return('Invalid cryptocurrency symbol')
  else:
    quote = json_data['data'][coin_symbol.upper()]

    return(format_quote(quote))

def up_or_down(num):
  if num > 0:
    return ':green_circle:'
  else:
    return ':small_red_triangle_down:'

def format_quote(quote):
  name = f'{quote["name"]} ({quote["symbol"]})'

  price = f'€ {round(quote["quote"]["EUR"]["price"], 2):,}'

  percent_change_1h_num = round(quote["quote"]["EUR"]["percent_change_1h"], 2)
  percent_change_1h = f'1h  {percent_change_1h_num}% {up_or_down(percent_change_1h_num)}'

  percent_change_24h_num = round(quote["quote"]["EUR"]["percent_change_24h"], 2)
  percent_change_24h = f'24h  {percent_change_24h_num}% {up_or_down(percent_change_24h_num)}'

  percent_change_7d_num = round(quote["quote"]["EUR"]["percent_change_7d"], 2)
  percent_change_7d = f'7d  {percent_change_7d_num}% {up_or_down(percent_change_7d_num)}'
    
  quote_string = f'{name}  |  {price}  |  {percent_change_1h}  |  {percent_change_24h}  |  {percent_change_7d}'

  return quote_string

scheduler = AsyncIOScheduler()
scheduler.add_job(job, "interval", hours=24)

scheduler.start()

keep_alive()

client.run(getEnvKey('TOKEN'))

asyncio.get_event_loop().run_forever()