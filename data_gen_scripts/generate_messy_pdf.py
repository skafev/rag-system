from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

output_dir = "documents/pdfs"
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, "messy_pdf.pdf")

c = canvas.Canvas(file_path, pagesize=letter)
width, height = letter
c.setFont("Helvetica", 12)

# Add messy content
c.drawString(50, height - 50, "Page 1")  # page marker
c.drawString(50, height - 80, "This   is   a   messy     PDF with inconsistent   spacing.")
c.drawString(50, height - 110, "•   Bullet one")
c.drawString(50, height - 140, "*   Bullet two")
c.drawString(50, height - 170, "Name     Age     Country")
c.drawString(50, height - 190, "Alice    30      USA")
c.drawString(50, height - 210, "Bob      25      UK")

c.save()

print("Messy PDF generated at:", file_path)
