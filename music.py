from datetime import datetime
from subprocess import call
from time import sleep
from os import listdir, path, walk
from threading import Thread, Event
from random import randint
import signal

from logger import Logger


__author__ = "Evgeny Goncharov"

log = Logger("/home/pi/AlarmClock/music.log")
log.info("Program start")

run_service = Event()
start_event = Event()
run_service.set()


def handler(signum, frame):
    run_service.clear()
    log.info("Signal to stop service {}".format(signum))


signal.signal(signal.SIGTERM, handler)


def stop_cvlc(start_event, run_service, log):
    while run_service.is_set():
        log.info("Stop-thread wait")
        start_event.wait()

        log.info("Stop-thread sleep")
        for i in range(60):
            if run_service.is_set():
                sleep(10)

        log.info("Killing cvlc")
        call(["killall", "vlc"])

        log.info("Stop-thread reset")
        start_event.clear()


Thread(target=stop_cvlc, args=(start_event, run_service, log)).start()


while run_service.is_set():
    start_path = "/media/Music"

    date = datetime.now()
    hour = date.hour
    minute = date.minute

    try:
        if (hour == 5 and minute >= 30) or (6 <= hour < 22):
            dirs = listdir(start_path)
            count_dirs = len(dirs)
            number_dir = randint(0, count_dirs - 1)
            dir = dirs[number_dir]
            log.info(dir)

            music_dir_path = None
            files = None
            count_files = None

            dir_found = False

            for i in range(5):
                music_dir_path = path.join(start_path, dir)

                files = next(walk(music_dir_path))[2]
                count_files = len(files)

                if count_files:
                    dir_found = True
                    break

                else:
                    dirs = listdir(music_dir_path)
                    count_dirs = len(dirs)
                    number_dir = randint(0, count_dirs - 1)
                    dir = dirs[number_dir]

                    start_path = music_dir_path

            if not dir_found:
                log.error("Directory have big deep: {}".format(music_dir_path))
                sleep(10)
                continue

            file_found = False

            for i in range(5):
                number_file = randint(0, count_files - 1)
                file = files[number_file]

                if (".mp3" in file) or (".flac" in file) or (".ape" in file):
                    file_found = True
                    break

            if not file_found:
                log.error("Directory don't have music files: {}".format(music_dir_path))
                sleep(10)
                continue

            log.info(file)
            music_file_path = path.join(music_dir_path, file)

            log.info("Event set")
            start_event.set()

            log.info("Start play music")
            call(["cvlc", music_file_path])

            log.info("Cvlc killed")
        else:
            sleep(10)
    except Exception as e:
        log.critical("!!!CRITICAL ERROR!!! {}".format(e))
        sleep(60)

log.info("Program stop\n")
