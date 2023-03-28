#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import *

import re

import requests


def get_token(password: str) -> str:
    header = {
        "Content-Type": "application/json",
        "password": password,
    }
    return requests.post("https://api.wikiwiki.jp/metroproj/auth", json=header, timeout=3.0).json()["token"]


def get_characters_page(token: str) -> Dict[str, str]:
    header = {
        "Authorization": f"Bearer {token}",
    }
    return requests.get(
        "https://api.wikiwiki.jp/metroproj/page/Metropolitan%20Project"
        "/%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC",
        headers=header,
    ).json()


def get_character(token: str, id_: str) -> str:
    context = get_characters_page(token)["source"]
    profile = re.finditer(
        r"\*\*\*(?P<name>.*?)\[#(?P<id>\w+)]\s(?P<names>(// names: .*?\s)?)"
        r"(?P<profile>(\|.*?\|.*?\|\s)+(.|\s)*?Made by \[\[.*?>メンバー#\w+]])",
        context,
    )
    for match in profile:
        names = []

        if m := match["names"]:
            for n in m[10:].split(","):
                names.append(n.strip().replace(" ", "").replace("・", ""))

        if m := re.fullmatch(r"(?P<name1>.*?)\((?P<name2>.*?)\)", match["name"].strip()):
            names.append(m["name1"].replace(" ", "").replace("・", ""))
            names.append(m["name2"].replace(" ", "").replace("・", ""))

        if id_.replace(" ", "").replace("・", "") in (
            match["id"].strip().strip(),
            match["name"].strip().replace(" ", "").replace("・", ""),
            *names,
        ):
            profile_match = re.fullmatch(
                r"(?P<datas>(\|.*?\|.*?\|\s)+)(?P<text>(.|\s)*?)Made by \[\[(?P<author>.*?)>メンバー#\w+]]",
                match["profile"].strip(),
            )
            data_text, text, author = (
                profile_match["datas"],
                profile_match["text"].strip(),
                profile_match["author"].strip(),
            )
            datas = re.finditer(r"\|(?P<key>.*?)\|(?P<value>.*?)\|\s", data_text)
            data = ""

            for d in datas:
                data += f"{d['key']}: {d['value']}\n"
            data = data.strip()
            return f"""{match["name"].strip()}(id: `{match["id"].strip()}`)

{data}

{text}

Made by {author}"""

    else:
        return f"'{id_}' is Not Found"
