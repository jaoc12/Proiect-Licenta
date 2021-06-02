from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import random
import os

digit_path = "../Date/Dataset/"


def create_sample(digit, it):
    """
    functie care genereaza o noua imagine cu o cifra data
    :param digit: ce cifra sa contina imaginea
    :param it: indicele cu care este salvata imaginea
    :return: nimic, imaginea generata este salvata ca fisier
    """
    # se alege un font in mod aleator
    fonts = ["calibri.ttf", 'arial.ttf', "verdana.ttf", "tahoma.ttf", "georgia.ttf"]
    choice = random.choice(fonts)

    # dimensiunea cifrei este 192(3/4 din 256)
    size = 192
    # pozitionarea cifrei este aleatoare
    origin = (random.randint(30, 120), random.randint(0, 20))

    # este creata o imagine 256x256 cu un singur canal de culoare
    img = Image.new('L', (256, 256))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(choice, size)

    # este amplasata cifra in imagine
    draw.text(origin, str(digit), fill=255, font=font)

    # imaginea este redimensionata si salvata
    img = img.resize((36, 36))
    img.save(digit_path + str(digit) + '/' + str(it) + '.jpg')


def create_dataset():
    """
    functie care creeaza 3000 de exemple pentru fiecare cifra de la 1 la 9
    :return: nimic
    """
    for digit in range(1, 10):
        for k in range(3000):
            create_sample(digit, k)
            print(digit, k)


create_dataset()
