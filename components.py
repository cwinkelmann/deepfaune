import PySimpleGUI as Sg
import io
import base64
from PIL import Image, ImageDraw


def StyledButton(button_text, fill, text_color, font=None, tooltip=None, key=None, visible=True,
              pad=None, bind_return_key=False, button_width=None):
    multi = 4
    btn_w = ((len(button_text) if button_width is None else button_width) * 5 + 20) * multi
    height = 18 * multi
    btn_img = Image.new('RGBA', (btn_w, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(btn_img)
    x0 = y0 = 0
    radius = 10 * multi
    d.ellipse((x0, y0, x0 + radius * 2, height), fill=fill)
    d.ellipse((btn_w - radius * 2 - 1, y0, btn_w - 1, height), fill=fill)
    d.rectangle((x0 + radius, y0, btn_w - radius, height), fill=fill)
    data = io.BytesIO()
    btn_img.thumbnail((btn_w // 3, height // 3), resample=Image.LANCZOS)
    btn_img.save(data, format='png', quality=100)
    btn_img = base64.b64encode(data.getvalue())
    return Sg.Button(button_text=button_text, image_data=btn_img, button_color=(text_color, text_color),
                     tooltip=tooltip, key=key, pad=pad, enable_events=False, size=(button_width, 1),
                     bind_return_key=bind_return_key, font=font, visible=visible, border_width=0)
