import urllib.request
import os

# Download the image from the user's upload (we'll use a placeholder approach)
# The image was provided inline - let's save it via Python

from fpdf import FPDF

img_path = "/home/user/Tee-es-t/candlelight_concert.jpg"
pdf_path = "/home/user/Tee-es-t/video_extract.pdf"

# Check if image exists
if not os.path.exists(img_path):
    print(f"Image not found at {img_path}")
    exit(1)

from PIL import Image
img = Image.open(img_path)
img_w, img_h = img.size

pdf = FPDF()
pdf.add_page()

# Add a title
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "YouTube Video Extract", ln=True, align="C")
pdf.ln(5)
pdf.set_font("Helvetica", "", 11)
pdf.cell(0, 8, "Source: https://www.youtube.com/watch?v=QkuOoRnrxSI", ln=True, align="C")
pdf.ln(10)

# Place small thumbnail at the bottom of the page
# Page dimensions: A4 = 210 x 297 mm, margins = 10mm
thumb_width = 50  # small thumbnail width in mm
aspect = img_h / img_w
thumb_height = thumb_width * aspect

# Position at the bottom center
x = (210 - thumb_width) / 2
y = 297 - thumb_height - 15  # 15mm from bottom

pdf.image(img_path, x=x, y=y, w=thumb_width)

# Add small caption under image
pdf.set_y(y + thumb_height + 2)
pdf.set_font("Helvetica", "I", 8)
pdf.cell(0, 5, "Candlelight Concert", align="C")

pdf.output(pdf_path)
print(f"PDF created: {pdf_path}")
