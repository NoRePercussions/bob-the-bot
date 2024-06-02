import discord
from discord.ext import commands
from openai import OpenAI
import os
import asyncio
import json
import argparse

SYSTEM_MESSAGE = "You are Bob. Do what people ask, say more than a few words, and ping people by their user_id, like <@000000000000000000>."


def is_dm(message):
    return isinstance(message.channel, discord.DMChannel) or isinstance(
        message.channel, discord.GroupChannel
    )


def run_bot(model, openai_key, token):
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)
    client = OpenAI(api_key=openai_key)

    @bot.event
    async def on_message(message):
        if (
            bot.user.mentioned_in(message)
            or is_dm(message)
            and not message.author == bot.user
        ):
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE,
                }
            ]

            msgs = [m async for m in message.channel.history(limit=10)]
            for msg in reversed(msgs):
                if msg.author == bot.user:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": f"{msg.content}",
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "user",
                            "content": f"{msg.author.name} <@{msg.author.id}>: {msg.content}",
                        }
                    )

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=150,
            )

            for msg in response.choices[0].message.content.split("\n"):
                await message.channel.send(msg)
        await bot.process_commands(message)

    bot.run(token)


def main():
    parser = argparse.ArgumentParser(description="Respond to messages as a bot.")
    parser.add_argument("model", type=str, help="OpenAI model checkpoint")
    parser.add_argument("openai_key", type=str, help="OpenAI API key")
    parser.add_argument("token", type=str, help="Discord bot token")

    args = parser.parse_args()
    asyncio.run(run_bot(args.model, args.openai_key, args.token))
