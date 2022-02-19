#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from pathlib import Path
from waveshare_epd import epd2in13b_V3
from typing import Tuple
import logging
import socket
import subprocess


@dataclass
class StatusBarState:
    local_ip: str
    wifi_name: str
    wifi_db: str


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_wifi_data() -> Tuple[str]:
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


def get_status_bar_state() -> StatusBarState:
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


@dataclass
class Text:
    draw: ImageDraw.Draw
    pos: Tuple[int]
    text: str
    font: ImageFont
    anchor: str = "lt"


def draw_text(t: Text) -> None:
    t.draw.text(t.pos, t.text, anchor=t.anchor, font=t.font, fill=0)


def draw_status_bar(
    epd: epd2in13b_V3.EPD,
    state: StatusBarState,
    resources_dir: Path,
) -> None:
    img_b = Image.new("1", (epd.height, epd.width), 255)
    img_r = Image.new("1", (epd.height, epd.width), 255)

    draw_b = ImageDraw.Draw(img_b)
    draw_r = ImageDraw.Draw(img_r)

    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    left_limit = 0
    print(font.getmask("hello world"))
    state_texts = (state.local_ip, state.wifi_name, state.wifi_db)
    state_texts_width = tuple(
        font.getmask(text).size[0] for text in state_texts
    )

    total_state_text_width = sum(state_texts_width)

    if total_state_text_width > epd.width:
        logging.info("status bar text longer than screen - cropping")
        hpad = 0
    else:
        # height instead of width because epd object assumes vertical rotation
        hpad = ((epd.height - total_state_text_width) / len(state_texts)) // 1

    for text, text_width in zip(state_texts, state_texts_width):
        draw_text(
            Text(
                draw=draw_b,
                pos=(left_limit, 0),
                text=text,
                font=font,
            )
        )
        left_limit += text_width + hpad

    epd.display(epd.getbuffer(img_b), epd.getbuffer(img_r))

    # logging.info("4.read bmp file on window")
    # blackimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # redimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # newimage = Image.open(str(resource_dir / "100x100.bmp"))
    # blackimage1.paste(newimage, (0, 0))
    # epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))


def main():
    status_bar_state = get_status_bar_state()
    epd = epd2in13b_V3.EPD()
    epd.init()
    epd.Clear()
    resources_dir = Path("./resources")
    logging.basicConfig(level=logging.DEBUG)

    try:
        draw_status_bar(epd, status_bar_state, resources_dir)
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
        exit()


if __name__ == "__main__":
    main()
