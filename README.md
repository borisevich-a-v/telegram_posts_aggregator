# telegram_posts_aggregator
Aggregate posts from several channels and send it via bot according the rules.


## Install dependencies
In the project [Poetry](https://python-poetry.org/) is used. Set up the project using [poetry guide](https://python-poetry.org/docs/basic-usage/#initialising-a-pre-existing-project)

## Setup environment
Create a .env file and fill in all required variables (see .env.example)
1. Create a bot in BotFather and fill in TELEGRAM_BOT_TOKEN
2. Create a new (!) account in Telegram and create API development tools https://my.telegram.org/.
    > Make sure that the account is not important for you, because Telegram often  bans accounts with API development tools for no reason.
3. Generate Client Session via utilities/generate_session.py and add it to .env
    > Keep in mind that you can't use the same session in multiple applications simultaneously. So it's recommended to create a session for every application (local setup, container setup, etc.)  

## Run the application in a container
```sh
docker compose build
docker compose up
```

### Run unit tests
You can choose any approach to run unit tests. We provide here two of them. <br>
**Approach 1 (terminal):** run `python -m pytest tests` in your terminal from the source root. <br>
**Approach 2 (PyCharm):** [read here](https://www.jetbrains.com/help/pycharm/testing.html)
