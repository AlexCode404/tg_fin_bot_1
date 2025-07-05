import magic
import os
from fpdf import FPDF

# Сохраняем оригинальную функцию
original_image_parsing = FPDF._parsejpeg if hasattr(FPDF, '_parsejpeg') else None
original_parse_png = FPDF._parsepng if hasattr(FPDF, '_parsepng') else None

# Замена функции определения типа изображения
def get_image_type(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    if file_type == 'image/jpeg':
        return 'JPEG'
    elif file_type == 'image/png':
        return 'PNG'
    elif file_type == 'image/gif':
        return 'GIF'
    return None

# Патч для метода image в FPDF
original_image = FPDF.image
def patched_image(self, name, x=None, y=None, w=0, h=0, type='', link=''):
    if type == '':
        ext = os.path.splitext(name)[1].lower()
        if ext == '.jpg' or ext == '.jpeg':
            type = 'JPEG'
        elif ext == '.png':
            type = 'PNG'
        else:
            type = get_image_type(name)
    return original_image(self, name, x, y, w, h, type, link)

# Применяем патч
FPDF.image = patched_image

print("FPDF патч для замены imghdr применен успешно") 