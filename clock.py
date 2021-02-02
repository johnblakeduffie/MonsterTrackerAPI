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


sched = BlockingScheduler()

# @sched.scheduled_job('interval', minutes=10)
# def timed_job():
#     print('This job is run every three minutes.')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=16, minute=51)
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
		#If monster hasn't already been added, and if the monster drops are not empty
		#if monster.wiki_name not in monsters and monster.drops:
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

	#print('This job is run every weekday at xx:xxpm.')

sched.start()