import json
import random
import requests

apikey = input("Data is drawn from 'https://www.alphavantage.co'. Use their API.\nWhat is your API? (WARNING: 25 a day limit per api, data is added every 5 minutes): ")
accounts = []

def stockpull(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol.upper(),
        'outputsize': 'compact',
        'interval': '5min',
        'apikey': apikey
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if 'Error Message' in data:
            print(f"Error from Alpha Vantage API: {data['Error Message']}")
            return None
        else:
            time_series_key = 'Time Series (5min)'
            latest_timestamp = next(iter(data[time_series_key]))
            latest_data = data[time_series_key][latest_timestamp]
            latest_price = float(latest_data['4. close'])

            return latest_price

    except requests.exceptions.RequestException as e:
        print('Error fetching data:', e)
        return None

def create_account(username):
    for acc in accounts:
        if acc['username'] == username:
            print(f"Username '{username}' already exists. Please choose another.")
            return
    
    new_account = {
        'username': username,
        'balance': 10000,
        'stocks': [],  # List to store owned stocks and their purchase prices
        'transactions': []
    }
    accounts.append(new_account)
    print(f"Account created for '{username}'.")

def get_user(username):
    for acc in accounts:
        if acc['username'] == username:
            return acc
    return None  # Return None if username not found

def display_balance(username):
    user = get_user(username)
    if user:
        print(f"Your current balance is: ${user['balance']}")
    else:
        print(f"User '{username}' not found.")

def show_owned_stocks(username):
    user = get_user(username)
    if user:
        if user['stocks']:
            print("Owned Stocks:")
            for stock in user['stocks']:
                print(f"{stock['symbol']}: Quantity - {stock['quantity']}, Average Price - ${stock['avg_price']}")
        else:
            print("You don't own any stocks.")
    else:
        print(f"User '{username}' not found.")

def buy_stock(username, symbol, quantity):
    user = get_user(username)
    if not user:
        print(f"User '{username}' not found.")
        return
    
    current_price = stockpull(symbol)
    if current_price is None:
        return
    
    total_cost = current_price * quantity

    if user['balance'] >= total_cost:
        # Deduct balance and log transaction
        user['balance'] -= total_cost
        # Check if the user already owns the stock
        owned_stock = next((stock for stock in user['stocks'] if stock['symbol'] == symbol), None)
        if owned_stock:
            # Update existing owned stock information
            old_value = owned_stock['avg_price'] * owned_stock['quantity']
            new_value = old_value + total_cost
            owned_stock['quantity'] += quantity
            owned_stock['avg_price'] = new_value / owned_stock['quantity']
        else:
            # Add new stock to user's portfolio
            user['stocks'].append({'symbol': symbol, 'quantity': quantity, 'avg_price': current_price})
        
        user['transactions'].append({'type': 'buy', 'symbol': symbol, 'quantity': quantity, 'price': current_price})
        print(f"Successfully bought {quantity} shares of '{symbol}' at ${current_price} each.")
    else:
        print(f"Insufficient balance to buy {quantity} shares of '{symbol}'.")

def sell_stock(username, symbol, quantity):
    user = get_user(username)
    if not user:
        print(f"User '{username}' not found.")
        return

    current_price = stockpull(symbol)
    if current_price is None:
        return

    # Check if the user owns the stock to sell
    owned_stock = next((stock for stock in user['stocks'] if stock['symbol'] == symbol), None)
    if not owned_stock or owned_stock['quantity'] < quantity:
        print(f"Insufficient shares of '{symbol}' to sell.")
        return

    # Calculate earnings and update balance
    total_earnings = current_price * quantity
    user['balance'] += total_earnings

    # Calculate profit or loss
    average_purchase_price = owned_stock['avg_price']
    total_purchase_value = average_purchase_price * quantity
    profit_loss = total_earnings - total_purchase_value

    # Log transaction
    user['transactions'].append({'type': 'sell', 'symbol': symbol, 'quantity': quantity, 'price': current_price})
    print(f"Successfully sold {quantity} shares of '{symbol}' at ${current_price} each.")
    print(f"Projected profit/loss: ${profit_loss}")

    # Update owned stocks
    if owned_stock['quantity'] == quantity:
        user['stocks'].remove(owned_stock)
    else:
        owned_stock['quantity'] -= quantity

def main():
    symbol = input("What is the stock you wish to view? ")
    latest_price = stockpull(symbol)
    if latest_price:
        print(f"The latest price of {symbol} is: ${latest_price}")

    while True:
        username = input("Which user are you? If none, say 'none' and we can make an account: ")
        if username.lower() == 'none':
            username = input("What do you want your username to be? ")
            create_account(username)
        else:
            user = get_user(username)
            if not user:
                print(f"User '{username}' not found. Please try again.")
                continue  # Loop back to ask for username again

        while True:
            print("\n1. Check Balance")
            print("2. Show Owned Stocks")
            print("3. Buy Stock")
            print("4. Sell Stock")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                display_balance(username)
            elif choice == '2':
                show_owned_stocks(username)
            elif choice == '3':
                symbol = input("Enter the stock symbol you want to buy: ")
                quantity = int(input("Enter the quantity you want to buy: "))
                buy_stock(username, symbol, quantity)
            elif choice == '4':
                symbol = input("Enter the stock symbol you want to sell: ")
                quantity = int(input("Enter the quantity you want to sell: "))
                sell_stock(username, symbol, quantity)
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()