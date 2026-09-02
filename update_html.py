import os

files = ['index.html', 'generator.html', 'history.html']
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace(
        '<script src="https://cdn.tailwindcss.com"></script>',
        '<script src="assets/vendor/tailwindcss.js"></script>'
    )
    content = content.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">',
        '<link href="assets/vendor/fonts.css" rel="stylesheet">'
    )
    content = content.replace(
        '<link href="https://cdn.jsdelivr.net/npm/simple-datatables@latest/dist/style.css" rel="stylesheet" type="text/css">',
        '<link href="assets/vendor/simple-datatables.css" rel="stylesheet" type="text/css">'
    )
    content = content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/simple-datatables@latest" type="text/javascript"></script>',
        '<script src="assets/vendor/simple-datatables.js" type="text/javascript"></script>'
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('HTML files updated successfully.')
