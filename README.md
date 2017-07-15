# MokouBot
A discord bot based on Chatterbot and discord.py

## Installation
Install python >= 3.5

##### Install dependencies:
```
pip install chatterbot discord.py
```

##### Download and install MongoDB:
https://www.mongodb.com/

##### In a terminal start MongoDB:
```
mongod --dbpath data/db/
```

## Running the bot

##### Train the bot:
The bot grabs conversations from threads on 4chan. You can configure from which board to get the data in config.py <br>
By default it grabs conversations from those boards:
```
SFW_BOARDS = ['jp', 'a', 'v',]
NSFW_BOARDS = ['b', 'pol']
```
The training script will also grab images from the SFW boards and place them in the images/ directory. If you do not want to download the images (1-2 GB), edit config.py and remove all the boards from SFW_BOARDS and place them in NSFW_BOARDS like so:
```
SFW_BOARDS = []
NSFW_BOARDS = ['jp', 'a', 'v', 'b', 'pol']
```
When ready start training:
```
python train.py
```

##### Get an API key
Create a new application here: https://discordapp.com/developers/applications/me#top <br>
Find the api key in the new application under Token and copy-paste it into a new file named API_KEY.txt located in the project root directory.<br>

##### Start the bot
```
python mokou.py
```

##### Invite the bot to your server
Go there and invite your bot: https://discordapp.com/oauth2/authorize?client_id={YOUR_CLIENT_ID}&scope=bot&permissions=0 <br>
Change {YOUR_CLIENT_ID} to the client ID of your bot
