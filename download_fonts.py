import os
import re
import urllib.request

CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
FONTS_DIR = "assets/vendor/fonts"
CSS_FILE = "assets/vendor/fonts.css"

if not os.path.exists(FONTS_DIR):
    os.makedirs(FONTS_DIR)

print("Downloading CSS...")
req = urllib.request.Request(CSS_URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as response:
    css_content = response.read().decode('utf-8')

urls = re.findall(r'url\((https://fonts\.gstatic\.com/s/[^\)]+)\)', css_content)
for i, url in enumerate(urls):
    filename = url.split('/')[-1]
    local_path = os.path.join(FONTS_DIR, filename)
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, local_path)
    css_content = css_content.replace(url, f"fonts/{filename}")

with open(CSS_FILE, "w", encoding="utf-8") as f:
    f.write(css_content)

print("Done!")
