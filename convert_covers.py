import os
import glob
from PIL import Image

cover_dir = os.path.expanduser('~/untitled_downloader/Cover art')
images = glob.glob(os.path.join(cover_dir, '*.*'))

for path in images:
    if not path.lower().endswith('.png'):
        print(f"Converting {os.path.basename(path)} to PNG")
        try:
            img = Image.open(path)
            if getattr(img, "is_animated", False):
                img.seek(0)
            img = img.convert('RGBA')
            new_path = os.path.splitext(path)[0] + '.png'
            img.save(new_path, "PNG")
            os.remove(path)
        except Exception as e:
            print(f"Error converting {path}: {e}")
