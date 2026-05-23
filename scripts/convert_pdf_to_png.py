import fitz # PyMuPDF

def pdf_to_png(pdf_path, output_path, page):
    # Open the PDF document
    doc = fitz.open(pdf_path)
    
    # Load the first page (0-indexed)
    page = doc.load_page(page) 
    
    # Set the resolution (zoom factor). 
    # 3.0 or 4.0 equals roughly 300-400 DPI, which is print-quality and very crisp.
    zoom_x = 8.0 
    zoom_y = 8.0 
    mat = fitz.Matrix(zoom_x, zoom_y)
    
    # Render the page to a pixmap (an image array)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    # Save directly to PNG
    pix.save(output_path)
    print(f"Saved high-res PDF conversion to {output_path}")

# Try it out
if(__name__ == '__main__'):
    pdf_to_png("DK Multimedia Proposal.pdf", f"DOC10.png", 0)
    ##for i in range(15, 24):
        ##pdf_to_png("LADR4e.pdf", f"DOC0{i-14}.png", i)