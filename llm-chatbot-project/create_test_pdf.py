from reportlab.pdfgen import canvas
from io import BytesIO

# Create a simple test PDF
buffer = BytesIO()
c = canvas.Canvas(buffer)
c.drawString(100, 750, "Test PDF Document")
c.drawString(100, 730, "This is a test PDF for the upload feature.")
c.showPage()
c.save()

# Save to file
with open('test.pdf', 'wb') as f:
    f.write(buffer.getvalue())
    
print("Test PDF created successfully")
