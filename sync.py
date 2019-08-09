#!/usr/bin/env python3.7
"""Google certified android devices tracker"""

import difflib
from datetime import date
from os import rename, path, system, environ
from requests import get, post

GIT_OAUTH_TOKEN = environ['GIT_OAUTH_TOKEN_XFU']
BOT_TOKEN = environ['bottoken']
TODAY = str(date.today())


def fetch():
    """
    Download latest and convert to markdown
    """
    url = "https://fast-fire-142512.appspot.com/_ah/api/catalogue/v1/devices"
    data = get(url).json()['items']
    data = sorted(data, key=lambda k: k['brand'])
    with open('README.md', 'w', encoding="utf-8") as markdown:
        markdown.write('# [Google Enterprise Android Devices List]'
                       '(https://androidenterprisepartners.withgoogle.com/devices/)\n\n')
        markdown.write('|Brand|Name|Models|Image|Type|'
                       'Display|RAM|Storage|OS|Telephony|Fingerprint|NFC|\n')
        markdown.write('|---|---|---|---|---|---|---|---|---|---|---|---|\n')
        for item in data:
            brand = item['brand']
            name = item['name']
            models = item['models']
            image = item['imageUrl']
            device_type = item['hardwareFeatures']['formFactor']
            display = item['hardwareFeatures']['display']
            ram = item['hardwareFeatures']['ram']
            flash = item['hardwareFeatures']['flash']
            os = item['hardwareFeatures']['os']
            telephony = ''
            try:
                if item['hardwareFeatures']['telephonySupport']:
                    telephony = '✓'
            except KeyError:
                telephony = '✗'
            fingerprint = ''
            try:
                if item['hardwareFeatures']['fingerprintSupport']:
                    fingerprint = '✓'
            except KeyError:
                fingerprint = '✗'
            nfc = ''
            try:
                if item['hardwareFeatures']['nfcSupport']:
                    nfc = '✓'
            except KeyError:
                nfc = '✗'
            markdown.write(f'|{brand}|{name}|{models}|[Here]({image})|{device_type}|{display}'
                           f'|{ram}|{flash}|{os}|{telephony}|{fingerprint}|{nfc}|\n')


def diff_files():
    """
    diff
    """
    with open('old.md', 'r') as old, open('README.md', 'r') as new:
        diff = difflib.unified_diff(old.readlines(), new.readlines(), fromfile='old', tofile='new')
    changes = [line.split('+')[1] for line in diff if line.startswith('+')]
    deletes = [line.split('-')[1] for line in diff if line.startswith('-')]
    adds = [line for line in changes[1:] if line not in deletes[1:]]
    new = ''.join(adds).replace("+", "")
    with open('changes', 'w') as out:
        out.write(new)


def post_to_tg():
    """
    post new devices to telegram channel
    """
    # tg
    telegram_chat = "@AndroidEnterpriseDevices"
    with open('changes', 'r') as f:
        changes = f.read()
    for line in changes.splitlines():
        info = line.split("|")
        brand = info[1]
        name = info[2]
        models = info[3]
        image = info[4]
        device_type = info[5]
        display = info[6]
        ram = info[7]
        flash = info[8]
        os = info[9]
        telephony = info[10]
        fingerprint = info[11]
        nfc = info[12]
        telegram_message = f"*New device added!* \n" \
            f"Brand: *{brand}*\n" \
            f"Name: *{name}*\n" \
            f"Type: *{device_type}*\n" \
            f"Models: `{models}`\n" \
            f"Image: {image}\n" \
            f"*Display*: {display}\n" \
            f"*RAM*: {ram}\n" \
            f"*Storage*: {flash}\n" \
            f"*OS*: {os}\n" \
            f"*Telephony Support*: {telephony}\n" \
            f"*Fingerprint Support*: {fingerprint}\n" \
            f"*NFC Support*: {nfc}\n"
        telegram_url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
        params = (
            ('chat_id', telegram_chat),
            ('text', telegram_message),
            ('parse_mode', "Markdown"),
            ('disable_web_page_preview', "yes")
        )
        telegram_req = post(telegram_url, params=params)
        telegram_status = telegram_req.status_code
        if telegram_status == 200:
            print("{0}: Telegram Message sent".format(name))
        else:
            print("Unknown error")


def git_commit_push():
    """
    git add - git commit - git push
    """
    system("git add README.md && git -c \"user.name=XiaomiFirmwareUpdater\" "
           "-c \"user.email=xiaomifirmwareupdater@gmail.com\" "
           "commit -m \"[skip ci] sync: {0}\" && "" \
           ""git push -q https://{1}@github.com/androidtrackers/"
           "android-enterprise-devices.git HEAD:master"
           .format(TODAY, GIT_OAUTH_TOKEN))


def main():
    """
    certified-android-devices tracker
    """
    if path.exists('README.md'):
        rename('README.md', 'old.md')
    fetch()
    diff_files()
    post_to_tg()
    git_commit_push()


if __name__ == '__main__':
    main()
