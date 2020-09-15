import random
from ...utilities import log


fs_coeffs_orig = [7.0, 3.0, 5.0, 1.0]
fs_coeffs = [7.0, 3.0, 5.0, 1.0]
applied_coeffs = [x / 16 for x in fs_coeffs]


class Dither:
    def __init__(self, pixels, width, height):
        self.orig_pixels = pixels.copy()
        self.pixels = pixels.copy()
        self.width = width
        self.height = height
        self.fs_dither_color()

    def index(self, y, x):
        return self.width * (self.height - y - 1) + x

    def apply_threshold(self, value, value_change):
        return round(value + value_change)

    def fs_dither_color(self):
        for y in range(0, self.height):
            for x in range(0, self.width):

                red_oldpixel, green_oldpixel, blue_oldpixel, alpha_oldpixel = self.pixels[self.index(y, x)]

                value_change = random.uniform(-0.2, 0.2)

                red_newpixel = self.apply_threshold(red_oldpixel, value_change)
                green_newpixel = self.apply_threshold(green_oldpixel, value_change)
                blue_newpixel = self.apply_threshold(blue_oldpixel, value_change)

                red_error = (red_oldpixel - red_newpixel) * 0.8
                blue_error = (blue_oldpixel - blue_newpixel) * 0.8
                green_error = (green_oldpixel - green_newpixel) * 0.8

                if self.height <= 4 and self.width <= 4:
                    log(f'{x},{y}')
                    log(f'{red_oldpixel},{green_oldpixel},{blue_oldpixel} -> {red_newpixel}, {green_newpixel}, {blue_newpixel}')
                    log(f'{self.pixels[self.index(y, x)]}')
                    log(f'ERROR: {red_error}, {blue_error}, {green_error}\n')

                self.pixels[self.index(y, x)] = float(red_newpixel) / 255, float(green_newpixel) / 255, float(blue_newpixel) / 255, float(alpha_oldpixel) / 255

                if x < self.width - 1:
                    red = self.pixels[self.index(y, x + 1)][0] + red_error * applied_coeffs[0]
                    green = self.pixels[self.index(y, x + 1)][1] + green_error * applied_coeffs[0]
                    blue = self.pixels[self.index(y, x + 1)][2] + blue_error * applied_coeffs[0]

                    self.pixels[self.index(y, x + 1)] = (red, green, blue, alpha_oldpixel)

                if x > 0 and y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x - 1)][0] + red_error * applied_coeffs[1]
                    green = self.pixels[self.index(y + 1, x - 1)][1] + green_error * applied_coeffs[1]
                    blue = self.pixels[self.index(y + 1, x - 1)][2] + blue_error * applied_coeffs[1]

                    self.pixels[self.index(y + 1, x - 1)] = (red, green, blue, alpha_oldpixel)

                if y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x)][0] + red_error * applied_coeffs[2]
                    green = self.pixels[self.index(y + 1, x)][1] + green_error * applied_coeffs[2]
                    blue = self.pixels[self.index(y + 1, x)][2] + blue_error * applied_coeffs[2]

                    self.pixels[self.index(y + 1, x)] = (red, green, blue, alpha_oldpixel)

                if x < self.width - 1 and y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x + 1)][0] + red_error * applied_coeffs[3]
                    green = self.pixels[self.index(y + 1, x + 1)][1] + green_error * applied_coeffs[3]
                    blue = self.pixels[self.index(y + 1, x + 1)][2] + blue_error * applied_coeffs[3]

                    self.pixels[self.index(y + 1, x + 1)] = (red, green, blue, alpha_oldpixel)
