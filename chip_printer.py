#!/usr/bin/env python3
# chip_printer.py
#
import math
from chip import Chip
from PIL import ImageFont, ImageDraw, Image

class ChipPrinter:
    config = {
        'dpi': 300,
        'fontSize': 1.0, # desired font size in mm but not really, font size is not an exact science
        'indentSize': 1.0,  # in mm
        'border': True,
        'font': 'fonts/CascadiaMono.ttf'
    }

    _chip = None
    _font = None

    def __init__(self):
        self._init_font()

    def _init_font(self):
        font_size = self._get_font_size()
        self._font = ImageFont.truetype(self.config['font'], font_size)

    def _draw_border(self, image):
        if self.config['border']:
            draw = ImageDraw.Draw(image)
            x,y = image.size
            draw.rectangle([(0,0), (x-1, y-1)])

    def _draw_chip_indent(self, image):
        _, canvasY = image.size
        indentPixels = self._get_indent_size()
        x0 = 0
        x1 = indentPixels
        y0 = (canvasY-indentPixels)//2
        y1 = y0 + indentPixels
        draw = ImageDraw.Draw(image)
        draw.line([(x0, y0), (x1//2, y0)])
        draw.line([(x0, y1), (x1//2, y1)])
        draw.arc([(x0, y0), (x1, y1)], 270, 90)

    def _draw_chip_name(self, image):
        _, canvasY = image.size
        draw = ImageDraw.Draw(image)
        x0 = math.ceil(self._get_indent_size() * 1.2)

        label = f'{self._chip.name} {self._chip.description}'

        _, textSizeY = draw.textsize(label, font=self._font)
        draw.text((x0, (canvasY-textSizeY)//2), label, font=self._font)

    def _draw_pins(self, image):
        canvasX, canvasY = image.size
        draw = ImageDraw.Draw(image)

        rows = len(self._chip) // 2
        pin = 1
        padding = 2 if self.config['border'] else 0
        for col in range(2):
            for row in range(rows):
                y = self._get_pin_row_y(row)
                if (col == 1):
                    y = canvasY-y
                pinName = self._chip[pin]
                invert = pinName[0] in ('~', '/', '!')
                pinName = pinName[1:] if invert else pinName
                pin += 1
                textSizeX, textSizeY = draw.textsize(pinName, font=self._font)
                offsetY = math.ceil(textSizeY / 2.0)
                x = padding
                if col == 1:
                    x = canvasX-textSizeX-padding
                draw.text((x, y-offsetY), pinName, font=self._font)
                if invert:
                    draw.line([(x,y-offsetY), (x+textSizeX, y-offsetY)])

    def _get_indent_size(self):
        return math.ceil(self.config['indentSize'] * self.config['dpi'] / 25.4)

    def _get_chip_size(self):
        width = self._chip.config['rowSpacing'] * self.config['dpi'] / 25.4
        height = (len(self._chip)//2) * self._chip.config['pinSpacing'] * self.config['dpi'] / 25.4
        return (math.ceil(width), math.ceil(height))

    def _get_pin_row_y(self, row):
        y = self._chip.config['pinSpacing'] * (row + 0.5) * self.config['dpi'] / 25.4
        return math.ceil(y)

    def _get_font_size(self):
        height = self.config['fontSize'] * self.config['dpi'] / 25.4
        return math.ceil(height)

    def print_chip(self, chip):
        self._chip = chip

        canvas_size = self._get_chip_size()

        image = Image.new(mode='1', size=canvas_size, color=255)

        self._draw_border(image)
        self._draw_pins(image)

        rotated = image.rotate(90, expand=True)

        self._draw_chip_name(rotated)
        self._draw_chip_indent(rotated)
        return rotated

def main(args):
    chip = Chip('7404', 14)
    pins = ['1A', '1Y', '2A', '2Y', '3A', '3Y', 'GND', '4Y', '4A', '5Y', '5A', '6Y', '6A', 'VCC']
    for pinnum, pin in enumerate(chip, 1):
        chip[pinnum] = pins[pinnum-1]

    printer = ChipPrinter()
    image = printer.print_chip(chip)
    image.save("./out.png", dpi=(printer.config['dpi'], printer.config['dpi']))

if __name__ == '__main__':
    import sys
    main(sys.argv)