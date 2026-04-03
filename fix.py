import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix duplicate "Other" input fields by finding consecutive duplicates
# Pattern: same input tag appearing twice in a row
def remove_duplicate_inputs(content):
    # Match pairs of identical input tags on adjacent lines
    pattern = r'(<input type="text" id="([^"]+)Other"[^/]*/>\n?)(\s*\1)'
    # Use a loop to remove duplicates
    prev = None
    while prev != content:
        prev = content
        content = re.sub(
            r'(<input type="text" id="([A-Za-z]+)Other"[^>]*/>\r?\n)([ \t]*\1)',
            r'\1',
            content
        )
    return content

html = remove_duplicate_inputs(html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done - duplicates removed")
