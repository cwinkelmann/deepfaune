from PIL import Image

def make_square(im, min_size=256, fill_color=(0, 0, 0)):
    x, y = im.size
    size = max(min_size, x, y)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im

test_image = Image.open('../testdata/loup.jpg')
new_image = make_square(test_image)
new_image.show()
