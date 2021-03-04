import configparser
from cryptography.fernet import Fernet

class Configurate(object):
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        self.host = self.cipher_suite.encrypt(b"SECRET")
        self.database = self.cipher_suite.encrypt(b"SECRET")
        self.user = self.cipher_suite.encrypt(b"SECRET")
        self.port = self.cipher_suite.encrypt(b"SECRET")
        self.password = self.cipher_suite.encrypt(b"SECRET")
        self.adminpass = self.cipher_suite.encrypt(b"SECRET")