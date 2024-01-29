import json
import subprocess
import schedule
import time
import discord
from discord.ext import tasks

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def check_and_send_new_transactions():
    print("Checking for new transactions...")
    # Load last checked transaction ID
    try:
        with open("last_checked_transaction_id.txt", "r") as file:
            last_checked_transaction_id = int(file.read())
    except FileNotFoundError:
        print("Last checked transaction ID file not found.")
        return

    # Load existing transactions from skyblock_banking.json
    try:
        with open("skyblock_banking.json", "r") as file:
            transactions = json.load(file)["transactions"]
    except FileNotFoundError:
        print("Skyblock banking file not found.")
        return

    # Filter new transactions based on last checked transaction ID
    new_transactions = [t for t in transactions if t["transaction_id"] > last_checked_transaction_id]

    if new_transactions:
        print(f"New transactions found: {new_transactions}")
        await send_to_discord(new_transactions)

        # Update last checked transaction ID
        last_checked_transaction_id = max(t["transaction_id"] for t in new_transactions)
        with open("last_checked_transaction_id.txt", "w") as file:
            file.write(str(last_checked_transaction_id))
        print("Last checked transaction ID updated.")
    else:
        print("No new transactions found.")

async def send_to_discord(new_transactions):
    try:
        print("Sending transactions to Discord...")
        channel_id = "123456"  # Replace 'YOUR_CHANNEL_ID' with the actual channel ID
        channel = client.get_channel(channel_id)
        if channel:
            for transaction in new_transactions:
                initiator_name = transaction.get("initiator_name", "Unknown")
                action = "deposited" if transaction.get("action").upper() == "DEPOSIT" else "withdrew"
                amount = int(transaction.get("amount", 0))
                balance_file = f"{initiator_name}.txt"
                with open(balance_file, "r") as file:
                    balance = int(file.read())
                    if action == "deposited":
                        balance += amount
                    elif action == "withdrew":
                        balance -= amount
                message = f"{initiator_name} {action} {amount / 1_000_000:.2f}M your current balance is {balance / 1_000_000:.2f}M"
                await channel.send(message)
                try:
                    with open(balance_file, "w") as file:
                        file.write(str(balance))
                    print(f"Balance updated: {balance}")
                except Exception as e:
                    print(f"Error updating balance: {e}")
            print("Messages sent successfully.")
        else:
            print("Channel not found.")
    except Exception as e:
        print(f"Error sending messages: {e}")

def run_bank():
    print("Running bank.py...")
    subprocess.run(["python", "bank.py"])

@client.event
async def on_ready():
    print(f"{client.user} is now running!")
    bank_task.start()

@tasks.loop(seconds=30)
async def bank_task():
    run_bank()
    await check_and_send_new_transactions()

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
        try: 
            client.run(TOKEN)
        except KeyboardInterrupt:
            client.close()
