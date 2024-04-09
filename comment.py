import re

with open('main.py', 'r') as file:
    content = file.read()

content_no_comments = re.sub(r'#.*$', "", content, flags=re.MULTILINE)

with open('main.py', 'w') as file:
    file.write(content_no_comments)
    print("Comments removed from main.py") 