

import keyring

def main():
    service = 'serial_device'

    login_id = input("Enter login ID: ")
    password = input("Enter password: ")

    keyring.set_password(service, 'login_id', login_id)
    keyring.set_password(service, 'password', password)
    print("Credentials saved securely in keyring.")

if __name__ == '__main__':
    main()
