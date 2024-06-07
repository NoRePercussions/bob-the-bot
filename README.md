# Bob the Bot
Run a finetuned ChatGPT Discord bot for less than $10!

Bob contains code necessary for scraping your server, finetuning
a model, and running a bot on the result. By default, it will respond
to pings and DMs/group messages.

## Usage

> [!TIP]
> Don't use Nix? You can install Poetry, setup with 
> `poetry install`, and substitute nix commands for:
> 
> - `poetry run bot <arguments>`
> - `poetry run scrape <arguments>`
> - `poetry run process <arguments`

### Bot

You must have an OpenAI API key with write permissions on "Model
capabilities" and a Discord bot key with at least the `message` and
`message_content` intents.

Run `nix run .#bot -- 'ft:gpt-3.5-turbo-0125' $OPENAI_API_KEY $DISCORD_BOT_TOKEN`. If you are
storing secrets in `.env`, you can do so with
`(set -a; source .env; set +a; nix run -- $DISCORD_BOT_TOKEN $OPENAI_API_KEY)`.

### Scraping and Training

1. Scrape with `nix run .#scrape -- $GUILD_ID messages.json $DISCORD_BOT_TOKEN`.
1. Process with `nix run .#process -- messages.json train.jsonl`.
1. Upload the training data to the [OpenAI Fine-Tuning Wizard](https://platform.openai.com/finetune)
1. Find your custom model name and use it instead of
   `ft:gpt-3.5-turbo-0125` when running the bot.


## Development

Python dependencies are managed with Poetry.

Packing and running are managed with Nix.

Lint your code with `nix run .#lint` before PRing.
