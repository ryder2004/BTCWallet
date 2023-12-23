import os
import sys
import subprocess
import qrcode
import blockcypher
from bitcoinlib.wallets import Wallet
from pycoingecko import CoinGeckoAPI
import colorama
from colorama import Fore, Style
import requests  # Added for update functionality

# Initialize Colorama
colorama.init(autoreset=False)

cg = CoinGeckoAPI()
api_key = '518638930e354dde938bed439b8e56be'

# Global variable for text color
current_text_color = Style.RESET_ALL

def clear_screen():
    global current_text_color
    input("Press Enter to continue...")
    os.system('clear' if os.name == 'posix' else 'cls')
    print(current_text_color, end="")

def display_menu():
    print("Bitcoin Wallet Menu:")
    print("1. Display Wallet Address")
    print("2. Display Wallet Balance (BTC and USD)")
    print("3. Send Bitcoin")
    print("4. Receive Bitcoin")
    print("5. Check Incoming Transactions")
    print("6. Get Current BTC Prices")
    print("7. Change Text Color")
    print("8. Update Libraries")
    print("9. Check for Updates")
    print("10. Quit")
    print("\n")
    print("Version 4.5 ALPHA")
    print("\n")
    print("Built By Eady Softwares")
    print("\n")

def get_user_choice():
    try:
        return int(input("Enter your choice (1-10): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return 0

def create_or_load_wallet(wallet_name):
    try:
        wallet = Wallet(wallet_name)
        print("Wallet Loaded.")
    except Exception as e:
        print(f"Error loading wallet: {e}")
        wallet = Wallet.create(wallet_name)
        print("New Wallet Created.")
    return wallet

def get_wallet_info(wallet, info_type):
    try:
        if info_type == 'address':
            return wallet.get_key().address
        elif info_type == 'balance':
            balance_satoshi = blockcypher.get_address_overview(wallet.get_key().address, api_key=api_key, coin_symbol='btc')['balance']
            balance_btc = balance_satoshi / 100000000  # Convert from satoshi to BTC
            btc_to_usd_rate = get_current_btc_prices()
            balance_usd = balance_btc * btc_to_usd_rate
            print(f"BTC Balance: {balance_btc} BTC (${balance_usd:.2f} USD)")
    except Exception as e:
        print(f"Error getting wallet {info_type}: {e}")
        return None

def get_transaction_fee():
    try:
        fee_stats = blockcypher.get_blockchain_overview(api_key=api_key)
        fee_per_byte = fee_stats['medium_fee_per_kb'] / 1024  # Convert from per KB to per byte
        estimated_tx_size = 250  # Average size in bytes
        return int(fee_per_byte * estimated_tx_size)  # Total fee in satoshis
    except Exception as e:
        print(f"Error retrieving transaction fee: {e}")
        return 0

def get_current_btc_prices():
    try:
        btc_price = cg.get_price(ids='bitcoin', vs_currencies='usd')['bitcoin']['usd']
        formatted_btc_price = f"${btc_price:,.2f}"  # Format price with commas and two decimal places
        print(f"{current_text_color}Current BTC Price: {formatted_btc_price}")
        return btc_price
    except Exception as e:
        print(f"Error getting BTC to USD price: {e}")
        return 0
def process_bitcoin_transaction(wallet, process_type, recipient_address=None, amount_to_send=None):
    global current_text_color
    try:
        if process_type == 'send':
            if not recipient_address or amount_to_send is None:
                raise ValueError("Recipient address and amount must be provided for sending BTC.")

            amount_to_send = float(amount_to_send)
            if amount_to_send <= 0:
                raise ValueError("Amount to send must be a positive number.")

            transaction_fee_satoshi = get_transaction_fee()
            transaction_fee_btc = transaction_fee_satoshi / 100000000  # Convert from satoshi to BTC
            btc_to_usd_rate = get_current_btc_prices()
            transaction_fee_usd = transaction_fee_btc * btc_to_usd_rate
            print(f"{current_text_color}Estimated Transaction Fee: {transaction_fee_btc} BTC (${transaction_fee_usd:.2f} USD)")
            
            confirm = input(f"Do you want to proceed with the transaction? (Transaction Fee: {transaction_fee_btc} BTC / ${transaction_fee_usd:.2f} USD) (y/n): ").lower()
            if confirm != 'y':
                print("Transaction cancelled.")
                return

            txid = wallet.send_to(recipient_address, amount_to_send, fee=transaction_fee_satoshi)
            print(f"Transaction sent. Transaction ID: {txid}")
        elif process_type == 'receive':
            new_address = wallet.get_key().address
            print(f"{current_text_color}New Receiving Address: {new_address}")
            if input("Generate QR code for this address? (y/n): ").lower() == 'y':
                generate_qr_code(new_address)
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"Error in transaction: {e}")

def generate_qr_code(address):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(address)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.show()

def check_incoming_transactions():
    global current_text_color
    address = '1MHdXjYEE1abKEYMGbYR13XanF9Ew89Xk7'  # Specific address to monitor
    try:
        txs = blockcypher.get_address_overview(address, api_key=api_key)
        if txs and 'unconfirmed_txrefs' in txs:
            for tx in txs['unconfirmed_txrefs']:
                amount = tx['value'] / 100000000  # Convert from satoshi to BTC
                print(f"{current_text_color}Incoming unconfirmed transaction: {amount} BTC")
        if txs and 'txrefs' in txs:
            for tx in txs['txrefs']:
                if tx['confirmations'] > 0:
                    amount = tx['value'] / 100000000  # Convert from satoshi to BTC
                    print(f"{current_text_color}Incoming confirmed transaction: {amount} BTC")
        else:
            print("No incoming transactions for this address.")
    except Exception as e:
        print(f"Error checking transactions: {e}")

def change_text_color():
    global current_text_color
    colors = {
        'Red': Fore.RED,
        'Green': Fore.GREEN,
        'Blue': Fore.BLUE,
        'Yellow': Fore.YELLOW,
        'Magenta': Fore.MAGENTA,
        'Cyan': Fore.CYAN,
        'White': Fore.WHITE,
        'Reset': Style.RESET_ALL
    }

    for i, color in enumerate(colors, 1):
        print(f"{i}. {color}")

    try:
        choice = int(input("Enter the number corresponding to the color: ")) - 1
        current_text_color = list(colors.values())[choice]
    except (IndexError, ValueError):
        print("Invalid color choice. Color not changed.")

def update_libraries():
    global current_text_color
    print("Updating libraries...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'bitcoinlib'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pycoingecko'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'qrcode'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'blockcypher'])
        print("Libraries updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update libraries: {e}")

def check_for_updates(current_version):
    version_url = "https://raw.githubusercontent.com/ryder2004/BTCWallet/main/Version.txt"
    try:
        response = requests.get(version_url)
        latest_version = response.text.strip()
        if latest_version > current_version:
            return latest_version
        else:
            return None
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None

def download_update(latest_version):
    download_url = f"https://github.com/ryder2004/BTCWallet/raw/main/app_v{latest_version}.zip"
    try:
        response = requests.get(download_url)
        download_path = os.path.join(os.path.expanduser('~'), f"app_v{latest_version}.zip")  # Save in the user's home directory
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"Update downloaded successfully to {download_path}.")
    except Exception as e:
        print(f"Error downloading update: {e}")

def main():
    global current_text_color
    wallet_name = 'your_wallet_name'  # Replace with your actual wallet name
    wallet = create_or_load_wallet(wallet_name)

    current_version = "5.2.TEST"  # Current version of your app

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == 1:
            print(f"{current_text_color}Wallet Address: {get_wallet_info(wallet, 'address')}")
        elif choice == 2:
            get_wallet_info(wallet, 'balance')
        elif choice == 3:
            recipient_address = input("Enter recipient address: ")
            amount_to_send = input("Enter amount to send: ")
            process_bitcoin_transaction(wallet, 'send', recipient_address, amount_to_send)
        elif choice == 4:
            process_bitcoin_transaction(wallet, 'receive')
        elif choice == 5:
            check_incoming_transactions()
        elif choice == 6:
            get_current_btc_prices()
        elif choice == 7:
            change_text_color()
        elif choice == 8:
            update_libraries()
        elif choice == 9:
            latest_version = check_for_updates(current_version)
            if latest_version:
                print(f"New version available: {latest_version}")
                user_confirmation = input("Do you want to download and install the update? (y/n): ").lower()
                if user_confirmation == 'y':
                    download_update(latest_version)
                    print("Please restart the application to complete the update.")
                else:
                    print("Update skipped.")
            else:
                print("No updates available.")
        elif choice == 10:
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 10.")

        clear_screen()

if __name__ == "__main__":
    main()
