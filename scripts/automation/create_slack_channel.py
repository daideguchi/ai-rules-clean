import os
import sys

import requests


def get_bot_user_id(token):
    """Gets the bot's own user ID."""
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    data = response.json()
    if data.get("ok"):
        user_id = data.get("user_id")
        print(f"✅ Successfully fetched bot user ID: {user_id}")
        return user_id
    else:
        print(f"❌ Failed to fetch bot user ID. Error: {data.get('error')}")
        return None

def create_slack_channel(token, channel_name):
    """Creates a new public Slack channel."""
    url = "https://slack.com/api/conversations.create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {"name": channel_name, "is_private": False}
    print(f"Attempting to create channel: #{channel_name}")
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if data.get("ok"):
        channel_id = data.get("channel", {}).get("id")
        print(f"✅ Successfully created channel with ID: {channel_id}")
        return channel_id
    else:
        error = data.get("error", "unknown_error")
        print(f"❌ Failed to create channel. Error: {error}")
        return None

def invite_bot_to_channel(token, channel_id, user_id):
    """Invites a user (the bot itself) to a channel."""
    url = "https://slack.com/api/conversations.invite"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {"channel": channel_id, "users": user_id}
    print(f"Attempting to invite bot ({user_id}) to channel: {channel_id}")
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if data.get("ok"):
        print("✅ Successfully invited bot to the channel.")
        return True
    else:
        error = data.get("error", "unknown_error")
        print(f"❌ Failed to invite bot. Error: {error}")
        return False

def post_slack_message(token, channel_id, text, channel_name_for_log):
    """Posts a message to a Slack channel."""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {"channel": channel_id, "text": text}
    print(f"Attempting to post message to channel ID: {channel_id}")
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if data.get("ok"):
        print(f"✅ Successfully posted message to channel #{channel_name_for_log}")
        return True
    else:
        print(f"❌ Failed to post message. Error: {data.get('error')}")
        return False

if __name__ == "__main__":
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN environment variable not set.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python create_slack_channel.py <channel_name> [optional_message]")
        sys.exit(1)

    channel_name = sys.argv[1]
    message_text = sys.argv[2] if len(sys.argv) > 2 else f"Channel '{channel_name}' created automatically."

    bot_user_id = get_bot_user_id(slack_token)
    if not bot_user_id:
        sys.exit(1)

    channel_id = create_slack_channel(slack_token, channel_name)
    if not channel_id:
        sys.exit(1)

    if not invite_bot_to_channel(slack_token, channel_id, bot_user_id):
        sys.exit(1)

    post_slack_message(slack_token, channel_id, message_text, channel_name)
