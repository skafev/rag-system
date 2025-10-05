import os

output_dir = "documents/html"
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, "messy_html.html")

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title> Messy   HTML   Example </title>
</head>
<body>
    <div class="nav">
        <ul>
            <li>Home</li>
            <li>About</li>
            <li>Contact</li>
        </ul>
    </div>

    <h1>   Messy   Article Title   </h1>
    <p>This   paragraph   has  too   much spacing.</p>
    <p>•   Bullet one</p>
    <p>*   Bullet two</p>

    <h2>   Data Table   </h2>
    <pre>
    Name    Age    Country
    Alice   30     USA
    Bob     25     UK
    </pre>
</body>
</html>
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Messy HTML generated at:", file_path)
