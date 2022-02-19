#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from pathlib import Path
from waveshare_epd import epd2in13b_V3
import logging
import socket
import subprocess


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


@dataclass
class StatusBarState:
    local_ip: str
    wifi_name: str
    wifi_db: str


def get_current_status_bar_state() -> StatusBarState:
    def get_iwlist_scan():
            universal_newlines=True,
        ).communicate()

    iwlist_out, iwlist_err = get_iwlist_scan()

    def get_wifi_data():
        proc= subprocess.Popen(
            ["iwlist", "wlan0", "scan"],
            stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if "Signal level" in line:
                db = line.split("=")[-1]
            elif "ESSID" in line:
                name = line.split('"')[1]
                break
        return name, db

    wifi_name, wifi_db = get_wifi_data(iwlist_out)

    return StatusBarState(
        local_ip=get_local_ip(),
        wifi_name=wifi_name,
        wifi_db=wifi_db,
    )


def draw_routine(resources_dir: Path) -> None:
    status_bar_state = get_current_status_bar_state()

    epd = epd2in13b_V3.EPD()
    point_centre = (epd.height // 2, epd.width // 2)
    epd.init()
    epd.Clear()

    # Drawing on the image
    logging.info("Drawing")
    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    HBlackimage = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new(
        "1", (epd.height, epd.width), 255
    )  # 298*126  ryimage: red or yellow image
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text(
        (0, 0), status_bar_state.local_ip, anchor="lt", font=font, fill=0
    )
    drawblack.text(
        (point_centre[0], 0),
        status_bar_state.wifi_name,
        anchor="mt",
        font=font,
        fill=0,
    )
    drawblack.text(
        (epd.width, 0),
        status_bar_state.wifi_db,
        anchor="rt",
        font=font,
        fill=0,
    )
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))

    # logging.info("4.read bmp file on window")
    # blackimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # redimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # newimage = Image.open(str(resource_dir / "100x100.bmp"))
    # blackimage1.paste(newimage, (0, 0))
    # epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))


def main():
    resources_dir = Path("./resources")
    logging.basicConfig(level=logging.DEBUG)

    try:
        draw_routine(resources_dir)
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
        exit()


if __name__ == "__main__":
    main()
