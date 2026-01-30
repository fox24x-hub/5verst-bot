#!/usr/bin/env python3
"""
Helper script to set up Telegram webhook for the bot.

Usage:
    python setup_webhook.py <telegram_bot_token> <webhook_url>

Example:
    python setup_webhook.py 123456789:ABCdefGHIjklmnoPQRstuvWXYZ https://5verst-bot-production.up.railway.app
"""

import requests
import sys
import os

def setup_webhook(token: str, webhook_url: str):
    """Set up Telegram webhook for the bot.
    
    Args:
        token: Telegram Bot API token
        webhook_url: Full webhook URL (e.g., https://example.com:443/webhook/telegram)
    """
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    # Telegram webhook path
    full_webhook = f"{webhook_url}/webhook/telegram"
    
    params = {
        "url": full_webhook,
        "max_connections": 40,
        "allowed_updates": ["message", "callback_query", "my_chat_member"]
    }
    
    print(f"Setting up webhook...")
    print(f"Webhook URL: {full_webhook}")
    print(f"API Endpoint: {api_url}")
    
    try:
        response = requests.post(api_url, json=params)
        result = response.json()
        
        if result.get("ok"):
            print("\n✅ Webhook successfully set!")
            print(f"Response: {result}")
            return True
        else:
            print(f"\n❌ Error: {result.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

def get_webhook_info(token: str):
    """Get current webhook information."""
    api_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        response = requests.get(api_url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print("\nCurrent webhook info:")
            print(f"  URL: {webhook_info.get('url', 'Not set')}")
            print(f"  Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"  Last error: {webhook_info.get('last_error_message', 'None')}")
            return webhook_info
        else:
            print(f"Error: {result.get('description')}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_webhook.py <telegram_bot_token> [webhook_url]")
        print("\nIf webhook_url is not provided, current webhook info will be displayed.")
        sys.exit(1)
    
    token = sys.argv[1]
    
    # Check current webhook
    print("Checking current webhook status...")
    get_webhook_info(token)
    
    # Set new webhook if URL provided
    if len(sys.argv) >= 3:
        webhook_url = sys.argv[2]
        if not webhook_url.startswith("http"):
            webhook_url = f"https://{webhook_url}"
        setup_webhook(token, webhook_url)
    else:
        print("\nTo set a new webhook, provide the URL:")
        print("python setup_webhook.py <token> <webhook_url>")
