#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
encrypt_config.py - 影视仓/TVBox 配置加密与 Base64 编码

影视仓/TVBox 支持两种“隐藏明文”的导入方式：
  1) Base64 编码：把整个 config.json 做 base64，得到一行文本。
  2) AES-128-ECB 加密：把 JSON 用密钥 AES-128-ECB(PKCS7) 加密后转 hex，
     导入时把 URL 填成密文文件地址，并在 App 里输入密钥即可解密。

用法：
    python3 scripts/encrypt_config.py config.json --mode base64
    python3 scripts/encrypt_config.py config.json --mode aes --key 你的密钥
    python3 scripts/encrypt_config.py config.json --mode all --key 你的密钥

输出：
    base64  -> config.base64.txt
    aes     -> config.enc(hex 密文) + 屏幕打印密钥/导入说明
仅依赖 Python 标准库。
"""
import argparse
import base64
import hashlib
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pkcs7_pad(b: bytes, block: int = 16) -> bytes:
    n = block - (len(b) % block)
    return b + bytes([n]) * n


def pkcs7_unpad(b: bytes) -> bytes:
    return b[:-b[-1]]


def derive_key(key: str) -> bytes:
    """密钥统一规范为 16 字节：16 字节直接用，否则取 md5。"""
    if len(key.encode()) == 16:
        return key.encode()
    return hashlib.md5(key.encode()).digest()


def aes_encrypt(data: bytes, key: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        sys.exit("需要 pip install cryptography")
    iv = b"\x00" * 16  # ECB 不需要 IV，占位
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    enc = cipher.encryptor()
    return enc.update(pkcs7_pad(data)) + enc.finalize()


def aes_decrypt(ct: bytes, key: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        sys.exit("需要 pip install cryptography")
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    dec = cipher.decryptor()
    return pkcs7_unpad(dec.update(ct) + dec.finalize())


def main():
    ap = argparse.ArgumentParser(description="影视仓配置加密/Base64 工具")
    ap.add_argument("input", help="输入的 JSON 配置文件")
    ap.add_argument("--mode", choices=["base64", "aes", "all"], default="base64",
                    help="base64=编码, aes=加密, all=两者都生成")
    ap.add_argument("--key", default="", help="AES 密钥(16字符；否则自动 md5 为 16 字节)")
    ap.add_argument("--out", help="输出目录，默认脚本同级的 outputs 子目录")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"文件不存在: {args.input}")
    data = open(args.input, "rb").read()
    out_dir = args.out or os.path.join(BASE, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if args.mode in ("base64", "all"):
        b64 = base64.b64encode(data).decode()
        with open(os.path.join(out_dir, "config.base64.txt"), "w") as f:
            f.write(b64)
        print("[OK] base64 已写入 outputs/config.base64.txt")
        print("     导入时把这一整行作为接口地址(或拼成 data:text/plain;base64, 前缀地址)。")

    if args.mode in ("aes", "all"):
        if not args.key:
            sys.exit("--mode aes 需要 --key")
        key = derive_key(args.key)
        ct = aes_encrypt(data, key)
        hextext = ct.hex()
        with open(os.path.join(out_dir, "config.enc"), "w") as f:
            f.write(hextext)
        print("[OK] AES-128-ECB 密文已写入 outputs/config.enc")
        print(f"     密钥: {args.key}  (派生字节: {key.hex()})")
        print("     使用方法: 把 config.enc 上传到任意静态托管(如本仓库)，"
              "导入地址填该文件 URL，App 弹出密钥时输入上面的密钥。")
        print("     注意: 密钥要自己保管好，丢了无法解密。")


if __name__ == "__main__":
    main()
