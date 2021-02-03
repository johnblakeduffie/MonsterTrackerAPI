# MonsterTrackerAPI

MonsterTrackerAPI is a django API for my monstertracker webapp => https://monstertracker.herokuapp.com/

This backend uses the Osrsbox monster database to see every monster in OSRS, and calculates their average income per kill
using the OSBuddy API for current price data. Each item that a monster drops adds to the total income.
The current calculation I use for the individual drops is: grossIncomePerKill = rarity * average sell price * average quantity * rolls

Images and wiki links were scraped using Selenium.

# Future Implementation:

Currently this API is hosted through heroku free tier, so I am constrained to a limited database space, and thus I am storing just the top
100 monsters for gross income per kill. I am also going to implement a cronjob with the logic from the updateProfit view to get the latest monster data.

# Current Problems:

Because the OSBuddy API returns only price from things sold in the last 5 min, so very rare/expensive items are left out in the calculation.
