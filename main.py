#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from inotify_simple import INotify, flags
from pathlib import Path
from typing import Tuple
from waveshare_epd import epd2in13b_V3
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


@dataclass
class Text:
    draw: ImageDraw.Draw
    pos: Tuple[int]
    text: str
    font: ImageFont
    anchor: str = "lt"
    def draw(self) -> None:
        self.draw.text(
            self.pos, self.text, anchor=self.anchor, font=self.font, fill=0
        )


def draw_status_bar(
    epd: epd2in13b_V3.EPD,
    state: StatusBarState,
    resources_dir: Path,
) -> int:
    img = Image.new("1", (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    left_limit = 0
    state_texts = (state.local_ip, state.wifi_name, state.wifi_db)
    state_texts_width = tuple(
        font.getmask(text).size[0] for text in state_texts
    )
    total_state_text_width = sum(state_texts_width)
    max_state_text_height = max(
        font.getmask(text).size[1] for text in state_texts
    )

    # height instead of width because epd object assumes vertical rotation
    if total_state_text_width > epd.height:
        logging.info("status bar text longer than screen - cropping")
        hpad = 1
    else:
        hpad = ((epd.height - total_state_text_width) / len(state_texts)) // 1

    # draw status bar text
    for text, text_width in zip(state_texts, state_texts_width):
        Text(
            draw=draw,
            pos=(left_limit, 0),
            text=text,
            font=font,
        ).draw()
        left_limit += text_width + hpad

    # draw status bar line
    line_height = max_state_text_height + 1
    draw.line((0, line_height, epd.height, line_height), fill=0)

    epd.display(
        epd.getbuffer(img),
        epd.getbuffer(Image.new("1", (epd.height, epd.width), 255)),
    )
    return line_height


def draw_event_bar(
    epd: epd2in13b_V3.EPD,
    event,
    resources_dir: Path,
    y: int,
    vpad: int = 2,
) -> int:
    event_flags = "    ".join(
        str(flag) for flag in flags.from_mask(event.mask)
    )
    text = f"{event.name}  {event_flags}"
    img = Image.new("1", (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    Text(
        draw=draw,
        pos=(0, y),
        text=text,
        font=font,
    ).draw()

    epd.display(
        epd.getbuffer(img),
        epd.getbuffer(Image.new("1", (epd.height, epd.width), 255)),
    )

    return font.getmask(text).size[1]


def main():
    status_bar_state = get_status_bar_state()
    epd = epd2in13b_V3.EPD()
    epd.init()
    epd.Clear()
    resources_dir = Path("./resources")
    logging.basicConfig(level=logging.DEBUG)

    inotify = INotify()
    watch_flags = (
        flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
    )
    wd = inotify.add_watch("downloads/", watch_flags)

    try:
        y = draw_status_bar(epd, status_bar_state, resources_dir)
        while True:
            events = inotify.read()
            for event in events:
                print(type(event))
                y = draw_event(epd, event, resources_dir, y)
                if y > epd.width:
                    epd.Clear()
                    y = draw_status_bar(epd, status_bar_state, resources_dir)
            time.sleep(1)

    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
        exit()


if __name__ == "__main__":
    main()
