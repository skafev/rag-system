from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

output_dir = "documents/pdfs"
os.makedirs(output_dir, exist_ok=True)

# Generate 30 sample PDFs
for i in range(1, 31):
    file_path = os.path.join(output_dir, f"sample_{i}.pdf")
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    text = f"""
    Report #{i}
    This is a sample PDF document generated for testing.
    It contains multiple lines of text to simulate a report.

    Section 1: Introduction
    This is the introduction of report {i}.

    Section 2: Data
    Here we would normally have some data tables or figures.

    Section 3: Conclusion
    This concludes the document.
    """

    c.drawString(100, 750, f"Sample PDF Report {i}")
    text_obj = c.beginText(80, 720)
    for line in text.split("\n"):
        text_obj.textLine(line.strip())
    c.drawText(text_obj)

    c.showPage()
    c.save()

print("30 PDFs generated in documents/pdfs/")
