#!/usr/bin/env python3
"""Avisa o IndexNow (Bing, Yandex e parceiros) das URLs do sitemap.xml.
Rodar DEPOIS do push, quando https://nitailab.com.br/<chave>.txt já responde 200.
Uso: python3 _fonte/indexnow.py   (na raiz do repo)"""
import json
import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "nitailab.com.br"
CHAVE = "e24c4607aa1032a0af6786adbadf35da"
LOCAL_CHAVE = f"https://{HOST}/{CHAVE}.txt"

urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(RAIZ, "sitemap.xml"), encoding="utf-8").read())
corpo = json.dumps({"host": HOST, "key": CHAVE, "keyLocation": LOCAL_CHAVE, "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=corpo, method="POST",
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow HTTP", r.status, f"({len(urls)} URLs)")
except urllib.error.HTTPError as e:
    print("IndexNow HTTP", e.code, f"({len(urls)} URLs)", e.read()[:200])
    sys.exit(1)
