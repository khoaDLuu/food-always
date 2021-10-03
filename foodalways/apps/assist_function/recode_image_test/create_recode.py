from PIL import Image, ImageDraw, ImageFont, ImageColor
import os, re
from django_food.settings import BASE_DIR
import random

def create_image_recode(number_a, number_b):
    """
    This code is borrowed from https://blog.csdn.net/jinixin/article/details/79248842
    """

    font_color = '#FFFFFF'

    image = Image.new(mode='RGBA', size=(52, 27))  # RGBA mode without color parameter --> a transparent image
    draw_table = ImageDraw.Draw(im=image)
    text = "{} + {}".format(number_a, number_b)
    draw_table.text(xy=(0, 0), text=text, fill=font_color, font=ImageFont.truetype('./msyh.ttc', 20))

    f_color_channel = ImageColor.getrgb(font_color)
    r, g, b, a = image.split()  # Split the image into three single-channel images

    # Iteratively process all pixels of the R/G/B channel image
    # and set them to the corresponding value of the font color
    r = r.point(lambda x: f_color_channel[0])
    g = g.point(lambda x: f_color_channel[1])
    b = b.point(lambda x: f_color_channel[2])

    image = Image.merge('RGBA', (r, g, b, a))  # merge the single-channel images into a new image

    # Generate random picture name
    name_str = 'ABCDEFGHIJKLMNOPQRETUVWXYZabcedfghijklmnopqrstuvwxyz0123456789_-'
    name = "".join(random.sample(name_str, 10))
    sql_info = (
        "INSERT INTO recode_image VALUES "
        "(<>, '{name}', {a}, {b}, 'recode_image/{name}.png', ".format(name=name, a=number_a, b=number_b)
        "'2021-07-01 09:32:27.012821');\n"
    )

    path = os.path.join(BASE_DIR, "media", "recode_image", "{}.png".format(name))
    image.save(path)
    image.close()

    return sql_info


if __name__ == '__main__':
    pattern = re.compile('<>')
    path_list = []
    for i in range(1, 10):
        for j in range(1, 10):
            path = create_image_recode(i, j)
            path_list.append(path)

    with open("recode_image.txt", "w") as f:
        count = 1
        for item in path_list:
            f.write(pattern.sub(str(count), item))
            count += 1
