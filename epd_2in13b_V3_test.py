#!/usr/bin/python
# -*- coding:utf-8 -*-


from pathlib import Path
import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
from dataclasses import dataclass


@dataclass
class Pair:
    x: int
    y: int

    def __post_init__(self):
        self.longest_dim = max(self.x, self.y)

def tuplize_pair(p: Pair):
    return p.x, p.y

class Display:
    """class to centre and scale objects on the screen"""

    def __init__(self, bottom_right: Pair):
        self.br = bottom_right
        self.tl = Pair(0, 0)
        self.tr = Pair(bottom_right.x, 0)
        self.bl = Pair(0, bottom_right.y)

    @classmethod
    def get_centre(self, size: Pair) -> Pair:
        if self.br.longest_dim < size.longest_dim:
            raise ValueError("size of object bigger than display")
        return Pair(round((self.br.x - size.x) / 2), round((self.br.y - size.y) / 2))


def draw_routine(resource_dir: Path) -> None:
    epd = epd2in13b_V3.EPD()
    display = Display(Pair(epd.width, epd.height))
    display_centre = (epd.height//2, epd.width//2)
    epd.init()
    epd.Clear()

    # Drawing on the image
    logging.info("Drawing")
    font20 = ImageFont.truetype(str(resource_dir / "Font.ttc"), 20)

    HBlackimage = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new(
        "1", (epd.height, epd.width), 255
    )  # 298*126  ryimage: red or yellow image
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text(display_centre, "hello world", font=font20, fill=0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))

    # logging.info("4.read bmp file on window")
    # blackimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # redimage1 = Image.new("1", (epd.height, epd.width), 255)  # 298*126
    # newimage = Image.open(str(resource_dir / "100x100.bmp"))
    # blackimage1.paste(newimage, (0, 0))
    # epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))


def main():
    resource_dir = Path("./pic")
    logging.basicConfig(level=logging.DEBUG)

    try:
        draw_routine(resource_dir)
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in13b_V3.epdconfig.module_exit()
        exit()


if __name__ == "__main__":
    main()
