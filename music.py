import signal
from datetime import datetime
from subprocess import call
from time import sleep
from os import listdir, path, walk
from threading import Thread, Event
from random import randint

from logger import Logger
from send_mail import send_mail

__author__ = "Evgeny Goncharov"

log = Logger("/home/pi/AlarmClock/music.log")
log.info("Program start")

run_service = Event()
start_event = Event()
run_service.set()


def handler(signum, frame):
    run_service.clear()
    log.debug("Signal to stop service {}".format(signum))


signal.signal(signal.SIGTERM, handler)


def stop_cvlc(start_event, run_service, log):
    while run_service.is_set():
        log.debug("Stop-thread wait")
        start_event.wait()

        log.debug("Stop-thread sleep")
        for i in range(60):
            if run_service.is_set():
                sleep(10)

        log.debug("Killing cvlc")
        call(["killall", "vlc"])

        log.debug("Stop-thread reset")
        start_event.clear()


Thread(target=stop_cvlc, args=(start_event, run_service, log)).start()


def find_file(start_path, name_dir):
    music_dir_path = path.join(start_path, name_dir)

    _, sub_dirs, files = next(walk(music_dir_path))

    count_sub_dirs = len(sub_dirs)
    count_files = len(files)

    if count_files:
        files = list(filter(
            lambda f: (".mp3" in f) or (".flac" in f) or (".ape" in f),
            files
        ))
        count_files = len(files)

    if count_sub_dirs == 0 and count_files == 0:
        return None

    file_or_dir = randint(0, count_sub_dirs + count_files - 1)

    if file_or_dir < count_sub_dirs:
        return find_file(music_dir_path, sub_dirs[file_or_dir])
    else:
        return path.join(music_dir_path, files[file_or_dir - count_sub_dirs])


while run_service.is_set():
    start_path = "/media/Music"

    date = datetime.now()
    hour = date.hour
    minute = date.minute

    if (hour == 5 and minute >= 30) or (6 <= hour < 22):
        try:
            dirs = listdir(start_path)
            count_dirs = len(dirs)
            number_dir = randint(0, count_dirs - 1)
            name_dir = dirs[number_dir]

            music_file_path = find_file(start_path, name_dir)

            if music_file_path:
                log.info("Music name: {}".format(music_file_path))

                log.debug("Event set")
                start_event.set()

                log.debug("Start play music")
                call(["cvlc", music_file_path])

                log.debug("Cvlc killed")

        except Exception as e:
            message = "!!!AlarmClock critical error!!! {}".format(e)
            log.critical(message)
            send_mail(message)
            sleep(60)

    else:
        sleep(10)

log.info("Program stop\n")
