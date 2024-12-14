import os
import requests
import json
import traceback
import time
import logging
from rocketchat_API.rocketchat import RocketChat

# Configure logging
LOG_FILE = "rocketchat_bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
ROCKETCHAT_URL = os.getenv("ROCKETCHAT_URL")
USERNAME = os.getenv("ROCKETCHAT_USERNAME")
PASSWORD = os.getenv("ROCKETCHAT_PASSWORD")
PUSHMORE_URL = os.getenv("PUSHMORE_URL")
INTERVAL = int(os.getenv("INTERVAL", "10"))
# Ensure recent_dms.json exists
DATA_FILE = "recent_dms.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump({}, file)
    logger.info(f"Created missing data file: {DATA_FILE}")

# Initialize RocketChat client using username and password

logger.info(f'Interval :{INTERVAL}')


def get_rocket_client():
    return RocketChat(USERNAME, PASSWORD, server_url=ROCKETCHAT_URL)

# Fetch all direct messages


def fetch_all_dms(rocket):
    try:
        all_dms = []
        offset = 0
        while True:
            response = rocket.im_list(count=100, offset=offset).json()

            if not response.get('success'):
                logger.error(f"Error fetching DMs: {
                             response.get('error', 'Unknown error')}")
                break

            ims = response.get('ims', [])
            all_dms.extend(ims)

            if len(ims) < 100:
                break

            offset += len(ims)

        all_dms = sorted(all_dms, key=lambda dm: dm.get(
            '_updatedAt', ""), reverse=True)
        logger.info(f"Total DMs fetched: {len(all_dms)}")
        return all_dms
    except Exception as e:
        logger.error("Error fetching all DMs:")
        logger.exception(e)
        return []

# Fetch recent messages from a room


def fetch_recent_messages(rocket, room_id, count=50):
    try:
        history_response = rocket.im_history(room_id, count=count).json()
        if not history_response.get('success', False):
            logger.error(f"Error fetching history for room {room_id}")
            return []
        return history_response.get('messages', [])
    except Exception as e:
        logger.error(f"Error fetching messages for room {room_id}:")
        logger.exception(e)
        return []

# Send a new message notification to Pushmore


def send_push_notification(message):
    try:
        response = requests.post(PUSHMORE_URL, data=message)
        response.raise_for_status()
    except Exception as e:
        logger.error("Error sending push notification:")
        logger.exception(e)

# Save the recent 50 messages for the 10 most recent DMs


def save_initial_messages(rocket, recent_dms):
    saved_data = {}
    for dm in recent_dms:
        room_id = dm.get('_id')
        usernames = dm.get('usernames', [])
        if not room_id or not usernames:
            logger.warning(
                f"Skipping DM due to missing '_id' or 'usernames': {dm}")
            continue

        messages = fetch_recent_messages(rocket, room_id, count=50)
        saved_data[room_id] = {
            "usernames": usernames,
            # Save only message IDs as a list
            "message_ids": list({msg['_id'] for msg in messages}),
            "messages": messages
        }

    with open(DATA_FILE, "w") as file:
        json.dump(saved_data, file, indent=4)
    logger.info("Initial messages saved successfully.")

# Compare saved messages with current messages and print new ones


def compare_and_print_new_messages(rocket, recent_dms):
    try:
        with open(DATA_FILE, "r") as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        logger.error(
            "No saved data found. Please run save_initial_messages first.")
        return

    for dm in recent_dms:
        room_id = dm.get('_id')
        usernames: list = dm.get('usernames', [])
        if not room_id or not usernames:
            logger.warning(
                f"Skipping DM due to missing '_id' or 'usernames': {dm}")
            continue

        # Initialize room data in saved_data if not already present
        if room_id not in saved_data:
            logger.info(f"No saved data for room_id={
                        room_id}. Initializing...")
            saved_data[room_id] = {
                "usernames": usernames,
                "message_ids": [],
                "messages": []
            }

        current_messages = fetch_recent_messages(rocket, room_id, count=50)
        saved_message_ids = set(saved_data[room_id].get("message_ids", []))

        for message in current_messages:
            if message['_id'] not in saved_message_ids:
                # Find the username that is not yours
                other_usernames = [
                    user for user in usernames if user != USERNAME]
                username = other_usernames[0] if other_usernames else "Unknown"

                new_message = f"""From {username}:\n\n{message['msg']}"""
                logger.info(new_message)
                send_push_notification(new_message)  # Send notification
                saved_data[room_id]["message_ids"].append(
                    message['_id'])  # Add new message ID

        # Update saved data with the latest messages
        saved_data[room_id] = {
            "usernames": usernames,
            "message_ids": saved_data[room_id]["message_ids"],
            "messages": current_messages
        }

    with open(DATA_FILE, "w") as file:
        json.dump(saved_data, file, indent=4)
    logger.info("New messages processed successfully.")


if __name__ == "__main__":
    logger.info("Starting RocketChat bot...")
    rocket = get_rocket_client()

    all_dms = fetch_all_dms(rocket)
    recent_dms = all_dms[:10]  # Take the 10 most recent DMs
    save_initial_messages(rocket, recent_dms)

    while True:
        all_dms = fetch_all_dms(rocket)
        recent_dms = all_dms[:10]  # Take the 10 most recent DMs
        compare_and_print_new_messages(rocket, recent_dms)
        time.sleep(INTERVAL)
