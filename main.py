#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from inotify_simple import Event, INotify, flags
from pathlib import Path
from typing import Tuple
from waveshare_epd import epd2in13b_V3
import logging
import time
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
    x: int
    y: int
    text: str
    font: ImageFont
    anchor: str = "lt"


def draw_text(t: Text) -> None:
    t.draw.text((t.x, t.y), t.text, anchor=t.anchor, font=t.font, fill=0)


@dataclass
class DrawReturn:
    img: Image
    y: int


def get_status_bar_draw_return(
    epd: epd2in13b_V3.EPD,
    state: StatusBarState,
    resources_dir: Path,
) -> DrawReturn:
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

    logging.info("getting status bar draw return")

    # height instead of width because epd object assumes vertical rotation
    if total_state_text_width > epd.height:
        logging.info("status bar text longer than screen - cropping")
        hpad = 1
    else:
        hpad = ((epd.height - total_state_text_width) / len(state_texts)) // 1

    # draw status bar text
    for text, text_width in zip(state_texts, state_texts_width):
        draw_text(
            Text(
                draw=draw,
                x=left_limit,
                y=0,
                text=text,
                font=font,
            )
        )
        left_limit += text_width + hpad

    # draw status bar line
    line_height = max_state_text_height + 1
    draw.line((0, line_height, epd.height, line_height), fill=0)

    return DrawReturn(img, line_height)


def get_event_draw_return(
    epd: epd2in13b_V3.EPD,
    event: Event,
    resources_dir: Path,
    y: int,
    img: Image,
    vpad: int = 5,
) -> DrawReturn:
    event_flags = " ".join(str(flag) for flag in flags.from_mask(event.mask))
    text = f"{event.name}  {event_flags}"
    draw = ImageDraw.Draw(img)
    font = ImageFont.load(str(resources_dir / "spleen-5x8.pil"))

    logging.info(f'getting draw return for event "{event.name}"')

    draw_text(
        Text(
            draw=draw,
            x=0,
            y=y,
            text=text,
            font=font,
        )
    )
    return DrawReturn(img, y + font.getmask(text).size[1])


def draw_img(img: Image, epd: epd2in13b_V3.EPD, is_black: bool = True) -> None:
    logging.info("drawing image")
    if is_black:
        epd.display(
            epd.getbuffer(img),
            epd.getbuffer(Image.new("1", (epd.height, epd.width), 255)),
        )
    else:
        epd.display(
            epd.getbuffer(Image.new("1", (epd.height, epd.width), 255)),
            epd.getbuffer(img),
        )


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
        dr = get_status_bar_draw_return(epd, status_bar_state, resources_dir)
        draw_img(dr.img, epd)
        while True:
            events = inotify.read()
            refreshed_drawing_events = False
            for event in events:
                dr = get_event_draw_return(
                    epd, event, resources_dir, dr.y, dr.img
                )
                if dr.y > epd.width:
                    refreshed_drawing_events = True
                    time.sleep(2)
                    epd.Clear()
                    dr = get_status_bar_draw_return(
                        epd, status_bar_state, resources_dir
                    )
            if not refreshed_drawing_events and len(events) > 0:
                draw_img(dr.img, epd)
            time.sleep(1)

    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
        exit()


if __name__ == "__main__":
    main()
