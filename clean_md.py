import os
import glob
import re

category_dir = 'category'
files = glob.glob(os.path.join(category_dir, '*.md'))

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace('<div class="ayat">', '').replace('</div>', '')
    
    if content != new_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'No changes needed for {file}')
