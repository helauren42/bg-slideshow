import random
import os
import sys
from time import sleep
import subprocess
import logging
from collections import deque
import signal

from database import database

USER_DIR = os.path.expanduser('~') + "/"
PROJECT_DIR = USER_DIR + ".local/appman/apps/bg-slideshow/"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_DIR + "logger.log", mode="a"),
    ]
)

# Log at launch
logging.info("Starting bg-slideshow application.")

# GLOBAL VARIABLES
imgs_history = deque()
db: database = database()

# CONST GLOBAL
HOME = os.path.expanduser("~")
LENGTH = 0 if db.imgs is None else len(db.imgs)
COLOR_SCHEME = subprocess.run(["gsettings get org.gnome.desktop.interface color-scheme"], shell=True,
                              stdout=subprocess.PIPE, text=True).stdout.strip()
COLOR_SCHEME = "dark" if COLOR_SCHEME.find("dark") != -1 else "light"

if not db.imgs or len(db.imgs) <= 0:
    print("No images have been found, can not activate")
    sys.exit(1)

def signalhandler(signum, frame):
    logging.info(f"Received signal: {signum}")
    logging.info(f"Signal caught in file: {frame.f_code.co_filename} at line: {frame.f_lineno}")
    sys.exit(0)

signal.signal(signal.SIGINT, signalhandler)
signal.signal(signal.SIGTERM, signalhandler)

def getImage():
    while len(imgs_history) > LENGTH // 2:
        imgs_history.popleft()
    img = None
    while img is None or img in imgs_history:
        i = random.randint(0, LENGTH -1)
        img = db.imgs[i]
    imgs_history.append(img)
    return img

def main():
    print("run main")
    while(True):
        img = getImage()
        img_path = db.path + "/" + img
        print(f"img_path: {img_path}")
        try:
            if COLOR_SCHEME == "dark":
                subprocess.run([f'gsettings set org.gnome.desktop.background picture-uri-dark {img_path}'], shell=True)
            else:
                subprocess.run([f'gsettings set org.gnome.desktop.background picture-uri {img_path}'], shell=True)
        except Exception as e:
            print("changing wallpaper failed:")
            print(e)
        sleep(db.time)

if __name__ == "__main__":
    main()
    logging.info("main ended")
