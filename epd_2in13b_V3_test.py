#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from pathlib import Path

picdir = Path("./pic")

import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in13b_V3 Demo")
    
    epd = epd2in13b_V3.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)
    
    # Drawing on the image
    logging.info("Drawing")    
    font20 = ImageFont.truetype( 'Font.ttc'), 20)
    
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...") 
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image  
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text((10, 0), 'hello world', font = font20, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    time.sleep(2)
    
    # logging.info("3.read bmp file")
    Blackimage = Image.open(str(picdir / '2in13bc-b.bmp'))
    RYimage = Image.open(str(picdir / '2in13bc-ry.bmp'))
    epd.display(epd.getbuffer(Blackimage), epd.getbuffer(RYimage))
    time.sleep(2)

    """    
    
    # logging.info("4.read bmp file on window")
    blackimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    redimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126    
    newimage = Image.open(os.path.join(picdir, '100x100.bmp'))
    blackimage1.paste(newimage, (0,0))
    epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))
    """    
    
    logging.info("Clear...")
    epd.init()
    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13b_V3.epdconfig.module_exit()
    exit()
