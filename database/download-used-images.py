import json
from subprocess import call
import os

with open('../app/static/data.json') as f:
    data = json.load(f)

images = set(e['photo_path'] for e in data.values())

for image in images:
    input_fn = 'hek:~/Documents/vibe-check/app/images/' + image
    directory, fn = os.path.split(image)
    output_dir = os.path.join('../app/images', directory)
    os.makedirs(output_dir, exist_ok=True)
    print(input_fn, output_dir)
    call(['scp', input_fn, output_dir])