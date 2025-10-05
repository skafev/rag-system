import os

output_dir = "documents/html"
os.makedirs(output_dir, exist_ok=True)

# Generate 30 sample HTML files
for i in range(1, 31):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Article {i}</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Article Title {i}</h1>
        <p>This is a sample HTML article. It simulates a web page with some structure.</p>

        <h2>Introduction</h2>
        <p>Welcome to article {i}. This section introduces the topic and provides context.</p>

        <h2>Main Content</h2>
        <p>The main body of the article contains detailed information.</p>
        <ul>
            <li>Key Point A</li>
            <li>Key Point B</li>
            <li>Key Point C</li>
        </ul>

        <h2>Conclusion</h2>
        <p>This concludes the article. Thank you for reading sample article {i}.</p>
    </body>
    </html>
    """

    file_path = os.path.join(output_dir, f"article_{i}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

print("30 HTML files generated in documents/html/")
