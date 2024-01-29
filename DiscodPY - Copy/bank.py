import json
import requests
import logging

# Configure logging
logging.basicConfig(filename='bank.log', level=logging.INFO)

# Load existing transactions from the JSON file
try:
    with open("skyblock_banking.json", "r") as file:
        existing_data = json.load(file)
        existing_transactions = existing_data["transactions"]
except FileNotFoundError:
    existing_transactions = []

# Load or initialize the transaction ID from a file
try:
    with open("transaction_id.txt", "r") as file:
        transaction_id = int(file.read())
except FileNotFoundError:
    transaction_id = 1

# API endpoint and parameters
api_url = "https://api.hypixel.net/v2/skyblock/profile"
api_key = 'THis is your api key'
profile_uuid = 'This is your profile UUID'

# Construct the URL with parameters
url = f"{api_url}?key={api_key}&profile={profile_uuid}"

# Send GET request to the API
response = requests.get(url)

# Check if request was successful
if response.status_code == 200:
    data = response.json()
    
    # Extract the "banking" array from the response
    new_transactions = data["profile"]["banking"]["transactions"]
    
    # Filter out transactions that are already in the existing array
    latest_timestamp = max(existing_transactions, key=lambda x: x["timestamp"])["timestamp"] if existing_transactions else 0
    new_transactions = [transaction for transaction in new_transactions if transaction["timestamp"] > latest_timestamp]

    # Add transaction ID, update the transaction ID counter, and remove "\u00a7" from initiator_name
    for transaction in new_transactions:
        transaction["transaction_id"] = transaction_id
        transaction_id += 1
        transaction["initiator_name"] = transaction["initiator_name"].replace("\u00a7", "")
        transaction["initiator_name"] = transaction["initiator_name"].replace("6", "")


    # Combine existing transactions with new transactions
    all_transactions = existing_transactions + new_transactions

    # Store the combined transactions in the desired format
    formatted_data = {"transactions": all_transactions}

    # Save the formatted data to a JSON file
    with open("skyblock_banking.json", "w") as file:
        json.dump(formatted_data, file, indent=2)

    # Save the updated transaction ID to a file
    with open("transaction_id.txt", "w") as file:
        file.write(str(transaction_id))

    # Log success
    logging.info("Data saved to skyblock_banking.json.")
else:
    # Log failure
    logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
