# Base-Aiogram-tasks-bot
## this bot provides a simple task management system, which allows you to add, delete, and mark tasks as completed.
## This bot is based on the aiogram library, postgresql, and sqlalchemy as ORM.
# Installation
### 1. install that project through git clone
```git clone https://github.com/DDJEDD/Base-Aiogram-tasks-bot```
### 2. install requirements
```pip install -r requirements.txt```
### 3. create a .env file in the root directory of the project and add the following:
```
NAME_OF_USER=your_name
PASSWORD_OF_USER=your_password
DATABASE_NAME=your_database_name
BOT_TOKEN=your_bot_token
```
### tip: BOT_TOKEN is the token of your bot, you can get it from @BotFather
### 4. create migrations
```alembic revision --autogenerate -m "migration"```
```alembic upgrade head```
### 5. run the main.py file
```python main.py```
# Created by DJED