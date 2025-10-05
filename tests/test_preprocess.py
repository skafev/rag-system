from app.utils.preprocess import preprocess

sample_text = """
--- Page 1 ---
This is a   test document.   

• Item one
* Item two
1. Numbered item

Table Example:
Name    Age    Country
Alice   30     USA
Bob     25     UK
"""

cleaned = preprocess(sample_text)

print("Cleaned text:\n")
print(cleaned)
