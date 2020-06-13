#!/usr/bin/env python3.7
"""Google certified android devices tracker"""

import difflib
from datetime import date
from itertools import tee
from os import rename, path, system, environ
from requests import get, post

GIT_OAUTH_TOKEN = environ['GIT_OAUTH_TOKEN_XFU']
BOT_TOKEN = environ['bottoken']
TODAY = str(date.today())


def fetch():
    """
    Download latest and convert to markdown
    """
    url = "https://androidenterprisepartners.withgoogle.com/_ah/spi/search/v1/devices?" \
          "aer=true&size=999&sort=aer:desc,sort_name:asc"
    data = get(url).json()['items']
    with open('README.md', 'w', encoding="utf-8") as markdown:
        markdown.write('# [Google Enterprise Android Devices List]'
                       '(https://androidenterprisepartners.withgoogle.com/devices/)\n\n')
        markdown.write('|Brand|Name|Models|Image|Website|Type|'
                       'Display|CPU|RAM|Storage|Battery|OS|Telephony|Fingerprint|NFC|\n')
        markdown.write('|---|---|---|---|---|---|---|---|---|---|---|---|\n')
        for item in data:
            brand = item['brand']
            name = item['name']
            models = item['models']
            image = item['imageUrls']['original']
            website = item['website']
            device_type = item['hardwareFeatures']['formFactor']
            display = item['hardwareFeatures']['display']
            ram = item['hardwareFeatures']['ram']
            flash = item['hardwareFeatures']['flash']
            os = item['hardwareFeatures']['os']
            processor_speed = item['hardwareFeatures']['processorSpeed']
            battery = item['hardwareFeatures']['batteryLife']
            telephony = '✓' if item['hardwareFeatures'].get('telephonySupport') else '✗'
            fingerprint = '✓' if item['hardwareFeatures'].get('fingerPrintSupport') else '✗'
            nfc = '✓' if item['hardwareFeatures'].get('nfcSupport') else '✗'
            markdown.write(f'|{brand}|{name}|{models}|[Here]({image})|[Here]({website})|{device_type}'
                           f'|{display}|{processor_speed}|{ram}|{flash}|{battery}|{os}'
                           f'|{telephony}|{fingerprint}|{nfc}|\n')


def diff_files():
    """
    diff
    """
    with open('old.md', 'r') as old, open('README.md', 'r') as new:
        diff = difflib.unified_diff(old.readlines(), new.readlines(), fromfile='old', tofile='new')
    d1, d2 = tee(diff, 2)
    changes = [line.split('+')[1] for line in d1 if line.startswith('+')]
    deletes = [line.split('-')[1] for line in d2 if line.startswith('-')]
    adds = [line for line in changes[1:] if '|'.join(line.split('|')[:3]) not in str(deletes[1:])]
    new = ''.join([i for i in changes if '|'.join(i.split('|')[:3]) in str(adds)])
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
        website = info[5]
        device_type = info[6]
        display = info[7]
        processor_speed = info[8]
        ram = info[9]
        flash = info[10]
        battery = info[11]
        os = info[12]
        telephony = info[13]
        fingerprint = info[14]
        nfc = info[15]
        telegram_message = f"*New Android Enterprise Recommended device added!*\n" \
            f"Brand: *{brand}*\n" \
            f"Name: *{name}*\n" \
            f"Type: *{device_type}*\n" \
            f"Models: `{models}`\n" \
            f"Website: {website}\n" \
            f"*Display*: {display}\n" \
            f"*CPU*: {processor_speed}\n" \
            f"*RAM*: {ram}\n" \
            f"*Storage*: {flash}\n" \
            f"*Battery*: `{battery}`\n" \
            f"*OS*: {os}\n" \
            f"*Telephony Support*: {telephony}\n" \
            f"*Fingerprint Support*: {fingerprint}\n" \
            f"*NFC Support*: {nfc}\n"
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto?" \
                       f"chat_id={telegram_chat}&caption={telegram_message}&" \
                       f"parse_mode=Markdown&disable_web_page_preview=yes&" \
                       f"photo={image.split('(')[1].split(')')[0]}"
        telegram_req = post(telegram_url)
        telegram_status = telegram_req.status_code
        if telegram_status == 200:
            print("{0}: Telegram Message sent".format(name))
        else:
            print(f"{telegram_req.reason}")


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
