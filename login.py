import sqlite3
import hashlib
import binascii
import os
from User import User
# user1 zaq1@WSX
# user2 ZAQ!2wsx


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


try:
    conn = sqlite3.connect('books.db')  # establishing database connection
    c = conn.cursor()
    c.execute("SELECT * FROM BOOKS")
    dump = c.fetchall()
except sqlite3.OperationalError:
    print("wyglada na to, ze cos sie zj*balo")
    exit()


login = input("Login: ")
password = input("Password: ")
loggingUser = User(login, password)
try:
    c.execute("SELECT password FROM users WHERE username=?", (login,))
except sqlite3.OperationalError:
    print('invalid user credentials')
    exit()
pwdCheck = c.fetchall()[0][0]
if verify_password(pwdCheck, password) is False:
    print('invalid user credentials')
    exit()
print('welcome ' + login)

