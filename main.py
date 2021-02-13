import os
from keep_alive import keep_alive
from discord.ext import commands
import discord
import requests
import json
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.api import N, W, wgs84, load
client = discord.Client()
bot = commands.Bot(
	command_prefix="!",  
	case_insensitive=True  
)
 
commands = {"**#Hello**":"Greet Cupcake!","#motivate":"Need for motivation? Cupcake's got your back.","#bodies -p <pageNumber 1-26>":"Get available body names"}
@bot.event 
async def on_ready():  
    print("I'm in")
    print(bot.user) 

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	elif message.content.startswith("#commands"):
		embed = discord.Embed(title="All Commands")
		for k,v in commands.items():
			embed.add_field(name=k,value=v,inline=False)
		await message.channel.send(embed=embed)
	elif message.content.startswith("#Hello"):
		await message.channel.send("Hello " + str(message.author).split("#")[0] +  " !")
	elif message.content.startswith("#motivate"):
		response = requests.get("https://zenquotes.io/api/random")
		jsonData = json.loads(response.text)
		quote = jsonData[0]['q']+" - "+jsonData[0]['a']
		await message.channel.send(quote)
	elif message.content.startswith("#bodies -p"):
		pageSize = 10
		page = int(str(message.content).split("-p")[1])
		if(page<1 or page>26):
			await message.channel.send("Page number can be in range [1-26]")
			return
		start = (page-1)*10
		end = (pageSize-1)+(pageSize*(page-1))
		response = requests.get("https://api.le-systeme-solaire.net/rest.php/bodies/")	
		jsonData = json.loads(response.text)
		names = []
		for i in range(start,end+1):
			names.append(jsonData["bodies"][i]["englishName"])
		jsonData = json.dumps(names, indent=2)
		print(jsonData)
		await message.channel.send(jsonData)
	elif message.content.startswith("#bodies -id"):
		id = str(message.content).split("-id")[1]
		print(id)
		response = requests.get("https://api.le-systeme-solaire.net/rest.php/bodies/")	
		jsonData = json.loads(response.text)
		bodies = jsonData["bodies"]
		value = next((x for x in bodies if x["englishName"] == (str(id)).strip().capitalize()), None)
		if(value==None):
			return 	await message.channel.send("Body with that name not found")
		else:
			value = json.dumps(value, indent=4)
			return await message.channel.send(value)
	elif message.content.startswith("#horoscope -t"):
	
		sign = str(message.content).split("-t")[1]
		print(sign)
		sign = (str(sign)).strip().capitalize()
		response = requests.get(f"http://horoscope-api.herokuapp.com/horoscope/today/{sign}")	
		jsonData = json.loads(response.text)
		value = jsonData["horoscope"]
		if(value==None):
			return 	await message.channel.send("Something went wrong")
		else:
			value = json.dumps(value, indent=4)
			embed = discord.Embed(title=f"Today's Horoscope for {sign}",description=value)
			return await message.channel.send(embed=embed)
	elif message.content.startswith("#horoscope -m"):
		embed = discord.Embed(title="All Commands")
		sign = str(message.content).split("-m")[1]
		print(sign)
		response = requests.get(f"http://horoscope-api.herokuapp.com/horoscope/month/{(str(sign)).strip().capitalize()}")	
		jsonData = json.loads(response.text)
		value = jsonData["horoscope"]
		if(value=="[]"):
			return 	await message.channel.send("Input valid sun sign")
		else:
			value = json.dumps(value, indent=4)
			embed = discord.Embed(title=f"Month Horoscope for {sign}",description=value)
			return await message.channel.send(embed=embed)
	elif message.content.startswith("#viewtime"):
		zone = timezone('US/Eastern')
		now = zone.localize(dt.datetime.now())
		midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
		next_midnight = midnight + dt.timedelta(days=1)

		ts = load.timescale()
		t0 = ts.from_datetime(midnight)
		t1 = ts.from_datetime(next_midnight)
		eph = load('de421.bsp')
		bluffton = wgs84.latlon(40.8939 * N, 83.8917 * W)
		f = almanac.dark_twilight_day(eph, bluffton)
		times, events = almanac.find_discrete(t0, t1, f)
		tstr=""
		for t, e in zip(times, events):
				tstr = tstr + f"{str(t.astimezone(zone))[:16]} {almanac.TWILIGHTS[e]}" + "\n"
		return await message.channel.send(tstr)
			


extensions = [
	'cogs.cog_example'  
]


if __name__ == '__main__':  
  client.run(os.getenv("TOKEN"))
  for extension in extensions:
    bot.load_extension(extension)  
    
keep_alive() 
token = os.environ.get("DISCORD_BOT_SECRET") 
bot.run(token) 