# Setting Up Your Telegram Bot

This guide will help you create a Telegram bot and get the required credentials for the price tracker.

## Step 1: Create a New Bot

1. Open Telegram on your phone or computer
2. Search for `@BotFather` (it's the official bot for creating other bots)
3. Start a conversation with BotFather
4. Send the command: `/newbot`
5. Follow the prompts:
   - **Bot name**: Choose a display name (e.g., "My Price Tracker")
   - **Bot username**: Choose a unique username ending in "bot" (e.g., "my_price_tracker_bot")
6. **Save the bot token!** BotFather will send you a message like:

```
Done! Congratulations on your new bot. You will find it at t.me/my_price_tracker_bot.
You can now add a description, about section and profile picture for your bot.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

The token looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Chat ID

### Option A: Using a Web Browser

1. Search for your bot by username in Telegram
2. Start a conversation with your bot
3. Send any message to your bot (e.g., "/start" or "Hello")
4. Open this URL in your web browser (replace `<BOT_TOKEN>` with your actual bot token):

```
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

5. You'll see a JSON response. Look for something like:

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {...},
        "chat": {
          "id": 987654321,  <-- This is your Chat ID!
          "first_name": "Your Name",
          "type": "private"
        },
        "date": 1234567890,
        "text": "/start"
      }
    }
  ]
}
```

6. **Save the Chat ID!** (the number in `"chat": {"id": 987654321}`)

### Option B: Using Command Line (curl)

```bash
curl https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

Look for the `chat.id` field in the JSON response.

### Option C: Using a Helper Bot

1. Search for `@userinfobot` in Telegram
2. Start a conversation
3. It will immediately send you your chat ID

## Step 3: Test Your Bot

Before deploying, verify your bot is working:

```bash
# Test the bot connection
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<CHAT_ID>", "text": "Hello from Price Tracker!"}'
```

You should receive a message from your bot in Telegram!

## Step 4: Configure Terraform

Add your bot credentials to `terraform/terraform.tfvars`:

```hcl
telegram_bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
telegram_chat_id   = "987654321"
```

**Important Security Notes:**
- Never commit your bot token to Git
- The `terraform.tfvars` file is already in `.gitignore`
- Keep your bot token secret - anyone with it can control your bot
- If you accidentally expose your token, use `/revoke` command with @BotFather to get a new one

## Troubleshooting

### Bot doesn't respond
- Make sure you've sent at least one message to the bot before trying to get updates
- Check that the bot token is correct (no extra spaces)
- Verify the bot is active in BotFather

### Can't find chat ID
- Make sure you sent a message to the bot first
- Try refreshing the `/getUpdates` URL
- The chat ID is always a positive number for private chats

### Getting "Forbidden" errors
- Verify the chat ID is correct
- Make sure you've started a conversation with the bot
- Check that the bot isn't blocked

## Next Steps

Once you have both values:
1. Update `terraform/terraform.tfvars` with your credentials
2. Continue with the deployment instructions in the main README
3. After deployment, you'll receive daily price updates from your bot!

## Optional: Customize Your Bot

You can enhance your bot using BotFather commands:
- `/setdescription` - Set bot description
- `/setabouttext` - Set "About" section text
- `/setuserpic` - Upload a profile picture
- `/setcommands` - Add custom commands

Example description:
```
I track product prices and send daily updates. Powered by AWS Lambda!
```
