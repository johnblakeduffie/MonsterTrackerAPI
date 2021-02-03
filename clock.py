from apscheduler.schedulers.blocking import BlockingScheduler
from monstertracker.serializers import MonsterSerializer, ProfitSerializer, DropSerializer, MonsterListSerializer
from monstertracker.models import Monster, Drop, MonsterList
import json
import operator
import requests
from urllib.request import urlopen
from osrsbox import monsters_api
from collections import OrderedDict
from operator import getitem


def retrievePrice(drop, marketDict):
	sell_average = 0
	if drop == "Coins":
		sell_average = 1
	else:
		for item in marketDict:
			item_id = item
			if marketDict[item_id]["name"] == drop:
				sell_average = marketDict[item_id]["sell_average"]
	return sell_average

def addToDropList(drop, sell_average):
	grossIncomePerKill = 0
	try:
		quantity = drop.quantity
		rarity = drop.rarity
		rolls = drop.rolls
		quantityAvg = 0.0
		if quantity.find('-') != -1:
			quantityRange = quantity.split('-')
			quantityAvg = (int(quantityRange[0]) + int(quantityRange[1])) / 2
		else:
			quantityAvg = int(quantity)
		grossIncomePerKill += rarity * float(sell_average) * quantityAvg * rolls
	except:
		grossIncomePerKill += 0
	updatedDrop = {'name' : drop.name, 'rarity' : rarity, 'sellAvg' : sell_average, 'quantityAvg' : quantityAvg, 'rolls' : rolls, 'grossIncomePerKill' : grossIncomePerKill}
	return updatedDrop

def updateDropList(name, rarity, rolls, quantityAvg, sell_average):
	grossIncomePerKill = 0
	try:
		grossIncomePerKill += rarity * float(sell_average) * quantityAvg * rolls
	except:
		grossIncomePerKill += 0
	updatedDrop = {'name' : name, 'rarity' : rarity, 'sellAvg' : sell_average, 'quantityAvg' : quantityAvg, 'rolls' : rolls, 'grossIncomePerKill' : grossIncomePerKill}
	return updatedDrop

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=12)
def scheduled_job():
	with urlopen("https://rsbuddy.com/exchange/summary.json") as marketResponse:
		marketSource = marketResponse.read()
		marketDict = json.loads(marketSource)
	monsterDict = monsters_api.load()
	monsters = []
	monsterProfitList = []
	sorted_monsterProfitDict = {}

	sep = '('

	for monster in monsterDict:
		name = monster.wiki_name.split(sep, 1)[0]
		if name not in monsters and monster.duplicate == False and monster.drops:
			monsters.append(name)
			totalProfit = 0
			drops = []
			for drop in monster.drops:
				updatedDrop = {}
				sell_average = retrievePrice(drop.name, marketDict)
				updatedDrop = addToDropList(drop, sell_average)
				drops.append(updatedDrop)
				totalProfit += updatedDrop["grossIncomePerKill"]
			monsterProfitList.append({'name' : name, 'grossIncomePerKill' : totalProfit, 'dropList' : drops})

	sorted_monsterProfitList = sorted(monsterProfitList, key = lambda i: i['grossIncomePerKill'], reverse=True)

	for monster in sorted_monsterProfitList:
		serializer = MonsterSerializer(data=monster)
		if serializer.is_valid():
			serializer.save()
		else:
			print("Invalid serializer: ")

sched.start()