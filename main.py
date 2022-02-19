#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from pathlib import Path
from waveshare_epd import epd2in13b_V3
import logging
import socket
import time
import traceback


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def draw_routine(resources_dir: Path) -> None:
    local_ip = get_local_ip()

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
    drawblack.text((0, 0), local_ip, anchor="lt", font=font, fill=0)
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
