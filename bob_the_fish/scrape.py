import discord
import asyncio
import json
import argparse


async def scrape(guild_id, output_file, token):
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

        guild = client.get_guild(guild_id)
        if guild is None:
            print(f"Guild with ID {guild_id} not found.")
            await client.close()
            return

        messages = []
        for channel in guild.text_channels:
            print(f"Scraping '{guild.name}'#'{channel.name}'")
            async for message in channel.history(limit=None):
                messages.append(
                    {
                        "timestamp": message.created_at.isoformat(),
                        "username": message.author.name,
                        "user_id": str(message.author.id),
                        "message_content": message.content,
                        # channel is annoying becuase it could be a guild
                        # channel, dm, thread, etc...
                        "channel_id": message.channel.id,
                    }
                )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        print("Scraping finished.")
        await client.close()

    await client.start(token)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape messages from a Discord guild."
    )
    parser.add_argument("guild_id", type=int, help="ID of the guild to scrape")
    parser.add_argument(
        "output_file", type=str, help="Output JSON file to save messages"
    )
    parser.add_argument("token", type=str, help="Discord bot token")

    args = parser.parse_args()
    asyncio.run(scrape(args.guild_id, args.output_file, args.token))
