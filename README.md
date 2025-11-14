# journalbot

Journalbot is a small command line tool that collects the most recent articles from a list of
journal RSS feeds and sends them to you via Telegram.

## Features

- Configure any number of journals via a simple YAML file.
- Fetch the latest entries from each feed using [feedparser](https://github.com/kurtmckee/feedparser).
- Aggregate the results into a single digest message.
- Deliver the digest to a Telegram chat or print it locally with `--dry-run`.

## Getting started

1. **Create a Telegram bot** using [@BotFather](https://core.telegram.org/bots/features#botfather)
   and note down the bot token. Start a chat with the bot so it can send you messages.
2. **Discover your chat ID.** An easy option is to message `https://api.telegram.org/bot<token>/getUpdates`
   after sending your bot a message and read the `chat.id` field from the JSON response.
3. **Install dependencies** and run the bot.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Copy `journals.example.yaml` to `journals.yaml` (or point the `--config` flag to any other file)
and customise the entries. Each journal entry must specify a human-friendly `name` and an RSS feed URL.

```yaml
journals:
  - name: My Favourite Journal
    feed_url: https://example.com/rss
    max_items: 3
  - name: Another Publication
    feed_url: https://another.example.com/feed

items_per_journal: 5
```

- `items_per_journal` controls how many entries are requested for each journal unless the
  individual entry specifies `max_items`.
- You can add or edit entries at any time – the bot simply reads the configuration file when it runs.

## Usage

Before running the bot set the Telegram credentials as environment variables or pass them on the command line:

```bash
export TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
export TELEGRAM_CHAT_ID=123456789
journalbot
```

The most common options are:

```bash
journalbot --config myjournals.yaml  # use a custom config file
journalbot --limit 2                 # override the number of posts per journal
journalbot --dry-run                 # print the digest instead of sending it
journalbot --token ... --chat-id ... # provide credentials explicitly
```

The command exits with a non-zero status if fetching feeds or sending the Telegram message fails, making it suitable for cron jobs or CI systems.

## Deploying from Cursor

Cursor ships with an integrated terminal, so you can deploy the bot without leaving the editor:

1. Open the terminal with <kbd>Ctrl</kbd> + <kbd>`</kbd> (``View → Terminal`` on macOS).
2. Create a virtual environment if you have not already done so and install the package:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. Copy `.env.example` to `.env` and fill in your Telegram bot token and chat ID. Cursor will automatically load the variables for shell sessions if you enable ``Terminal › Integrated: Allow Workspace Configuration`` in settings, or you can source the file manually: `set -a && source .env && set +a`.
4. Edit `journals.yaml` (or your custom config) inside Cursor. The bot reads this file every time it runs, so changes are applied immediately.
5. Run the command from the terminal:

   ```bash
   journalbot --config journals.yaml
   ```

Cursor remembers the previous commands, making it easy to re-run the bot whenever you need an updated digest.

## Scheduling options

Once you are happy with the configuration, automate the command so it runs on a schedule.

### Cron (local or server)

Add an entry like the following to your crontab (`crontab -e`). This example runs the bot every weekday at 8am:

```cron
0 8 * * 1-5 cd /path/to/journalbot && . .venv/bin/activate && set -a && source .env && set +a && journalbot --config journals.yaml >> journalbot.log 2>&1
```

### GitHub Actions (hosted)

If your configuration lives in a Git repository, you can use the provided workflow at `.github/workflows/journalbot.yaml` as a starting point. Store the Telegram credentials as repository or organization secrets (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) and commit your `journals.yaml` file. The workflow runs on the schedule defined in the file and sends the digest without maintaining your own server.
