#!/usr/bin/env python3
"""Experimental legacy encoding helper; client compatibility is NOT guaranteed.
Base64 is not encryption. AES-ECB is a legacy compatibility format, not secure storage.
Never publish passwords/tokens in a public repository, even encoded.
Optional AES dependency: pip install cryptography
"""
import argparse
import base64
import getpass
import hashlib
import json
import os
from pathlib import Path


def pkcs7_pad(data, block=16):
    count = block - len(data) % block
    return data + bytes([count]) * count


def pkcs7_unpad(data):
    if not data or len(data) % 16:
        raise ValueError('invalid padded length')
    count = data[-1]
    if not 1 <= count <= 16 or data[-count:] != bytes([count]) * count:
        raise ValueError('invalid padding or key')
    return data[:-count]


def derive_key(key):
    encoded = key.encode('utf-8')
    if not encoded:
        raise ValueError('empty key')
    return encoded if len(encoded) == 16 else hashlib.md5(encoded).digest()


def aes_encrypt(data, key):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return encryptor.update(pkcs7_pad(data)) + encryptor.finalize()


def aes_decrypt(data, key):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return pkcs7_unpad(decryptor.update(data) + decryptor.finalize())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--mode', choices=('base64', 'aes', 'all'), default='base64')
    parser.add_argument('--key-env', default='YSC_CONFIG_KEY', help='environment variable name, not the secret')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1] / 'outputs')
    args = parser.parse_args()
    data = args.input.read_bytes()
    parsed = json.loads(data.decode('utf-8-sig'))
    if not isinstance(parsed, dict):
        parser.error('input must be a JSON object')
    outputs = {}
    if args.mode in ('aes', 'all'):
        secret = os.environ.get(args.key_env) or getpass.getpass('AES key (not logged): ')
        outputs['config.enc'] = aes_encrypt(data, derive_key(secret)).hex()
    if args.mode in ('base64', 'all'):
        outputs['config.base64.txt'] = base64.b64encode(data).decode('ascii')
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in outputs.items():
        (args.out / name).write_text(value, encoding='utf-8')
        print('Written: ' + str(args.out / name))
    print('Experimental output only. Verify client support; do not publish secrets.')


if __name__ == '__main__':
    main()
