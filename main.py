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


def get_wifi_data():
    proc = subprocess.Popen(
        ["iwlist", "wlan0", "scan"], stdout=subprocess.PIPE
    )
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if b"Signal level" in line:
            db = line.decode("ascii").strip().split("=")[-1]
        elif b"ESSID" in line:
            name = line.decode("ascii").strip().split('"')[1]
            break
    return name, db


def get_current_status_bar_state() -> StatusBarState:
    wifi_name, wifi_db = get_wifi_data()

    return StatusBarState(
        local_ip=get_local_ip(),
        wifi_name=wifi_name,
        wifi_db=wifi_db,
    )


def get_horiz_padding(d: ImageDraw.Draw, px_pad: int = 5) -> int:
    _, _, width, _ = d.getbbox()
    return width + px_pad


def get_vert_padding(d: ImageDraw.Draw, px_pad: int = 2) -> int:
    _, _, _, vert = d.getbbox()
    return vert + px_pad


def draw_routine(resources_dir: Path) -> None:
    status_bar_state = get_current_status_bar_state()

    epd = epd2in13b_V3.EPD()
    point_centre = (epd.height // 2, epd.width // 2)
    epd.init()
    epd.Clear()

    logging.info("Drawing")
    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    img_b = Image.new("1", (epd.height, epd.width), 255) 
    img_r = Image.new("1", (epd.height, epd.width), 255)

    draw_b = ImageDraw.Draw(img_b)
    draw_r = ImageDraw.Draw(img_r)

    draw_b.text(
        (0, 0), status_bar_state.local_ip, anchor="lt", font=font, fill=0
    )

    draw_b.text(
        (get_horiz_padding(img_b), 0),
        status_bar_state.wifi_name,
        anchor="lt",
        font=font,
        fill=0,
    )
    draw_b.text(
        (get_horiz_padding(img_b), 0),
        status_bar_state.wifi_db,
        anchor="lt",
        font=font,
        fill=0,
    )
    epd.display(epd.getbuffer(img_b), epd.getbuffer(img_r))

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
