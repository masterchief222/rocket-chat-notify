# Rocket.Chat to Telegram Notification Bot

## Overview
This project is a bot that listens to new messages in Rocket.Chat direct messages (DMs) and sends them to a Telegram chat using a Push Bot (such as [Pushmore](https://pushmore.io)). It is designed to monitor new activity in Rocket.Chat and relay important messages to your Telegram channel or group.

## Features
- Fetches new messages from Rocket.Chat DMs.
- Excludes your own messages when detecting new messages.
- Sends notifications for new messages via a Push Bot (e.g., [Pushmore](https://pushmore.io)).
- Includes sender information for better context.

## How It Works
1. The bot connects to your Rocket.Chat instance using API credentials.
2. It monitors the most recent DMs for new messages.
3. When a new message is detected:
   - The bot identifies the sender (excluding your username).
   - Sends a notification to Telegram via a Push Bot API.
4. Logs all activities, errors, and notifications.

## Prerequisites
- A Rocket.Chat instance with API access enabled.
- A Push Bot webhook URL (e.g., Pushmore webhook).
- Python 3.12 or above.
- Docker (optional, for containerized deployment).

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies
#### Option 1: Install Locally
```bash
pip install -r requirements.txt
```

#### Option 2: Use Docker
Build and run the container:
```bash
docker-compose up --build
```

### 3. Environment Variables
Create a `.env` file or set the following environment variables:
```env
ROCKETCHAT_URL=https://your-rocketchat-instance.com
ROCKETCHAT_USERNAME=your_username
ROCKETCHAT_PASSWORD=your_password
PUSHMORE_URL=https://pushmore.io/webhook/your-webhook
```

### 4. Run the Bot
#### Locally
```bash
python rocket_chat.py
```
#### Using Docker
```bash
docker-compose up
```

## Configuration
The bot uses the following environment variables:
- `ROCKETCHAT_URL`: The URL of your Rocket.Chat instance.
- `ROCKETCHAT_USERNAME`: Your Rocket.Chat username.
- `ROCKETCHAT_PASSWORD`: Your Rocket.Chat password.
- `PUSHMORE_URL`: The webhook URL for your Push Bot.

## Code Structure
- `rocket_chat.py`: The main script containing bot logic.
- `requirements.txt`: Dependencies required for the project.
- `docker-compose.yml`: Docker configuration for containerized deployment.
- `rocketchat_bot.log`: Log file (generated at runtime).

## Logging
Logs are saved to `rocketchat_bot.log` and printed to the console. They include:
- Successful notifications.
- Errors when fetching messages or sending notifications.
- Skipped DMs with missing or invalid data.

## Example Workflow
1. A user sends a DM to you in Rocket.Chat.
2. The bot detects the new message and identifies the sender.
3. The message is sent to your Telegram chat via the Push Bot webhook.
4. Logs record the notification event.

## Contributing
Feel free to fork the repository and submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.

## Support
If you encounter any issues, please create an issue in the repository or contact the project maintainer.

