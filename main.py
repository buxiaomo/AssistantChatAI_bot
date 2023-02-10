#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import openai
import telebot
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


engine = create_engine(f'sqlite:////app/db/chatgpt.sqlite3')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(os.getenv("TELEGRAM_API_KEY"), parse_mode=None)
openai.api_key = os.getenv("OPENAI_API_KEY")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    cid = message.chat.id
    session = DBSession()
    chat = session.query(Chat).filter(Chat.name == cid).first()
    if chat is None:
        new_user = Chat(name=cid)
        session.add(new_user)
        session.commit()
    session.close()
    bot.reply_to(message, "这是一个基于ChatGPT的聊天机器人, 目前仅支持一问一答, 不支持上下文理解\n代码地址: https://github.com/buxiaomo/AssistantChatAI_bot.git, 欢迎补充功能. \n现在你可以和我聊天了。")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    cid = message.chat.id

    cInfo = bot.get_chat(cid)

    session = DBSession()
    chat = session.query(Chat).filter(Chat.name == cid).first()
    if chat is None:
        new_user = Chat(name=cid)
        session.add(new_user)
        session.commit()
    session.close()

    # q_embeddings = openai.Embedding.create(input=message.text, engine='text-embedding-ada-002')['data'][0]['embedding']
    # print(q_embeddings)

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=message.text,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5
        )
        text = response["choices"][0]["text"].strip()
        bot.reply_to(message, text)
        logger.info(json.dumps({
            "first_name": cInfo.first_name,
            "last_name": cInfo.last_name,
            "chat_id": cid,
            "message": message.text,
            "reply": text
        }, ensure_ascii=False))
    except Exception as e:
        bot.reply_to(message, e)


bot.infinity_polling()
