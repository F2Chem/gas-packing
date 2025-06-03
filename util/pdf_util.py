import datetime
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.graphics.shapes import *
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

TABLE_ROW_UNIT = 30
TABLE_COL_UNIT = 40
PADDING = 5
LEFT = 20
TOP = 550
MAX_FONT_SIZE = 10
MIN_FONT_SIZE = 5


# Just a test thing created as I learn how to do PDFs!
def create_pdf(data):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setPageSize( (height, width) )
    p.setTitle(data['title'])
    #print(p.getAvailableFonts ())

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFillColorRGB(0, 0, 0.5)
    p.setStrokeColorRGB(0.5, 0, 0)
    p.setFont("Times-Roman", 16,leading=None)
    p.drawString(100, 500, "Hello world.")
    p.line(100, 490, 300, 490)


    style = getSampleStyleSheet()["Normal"]

    text = """You can't have it both ways. Either your text is pre-formatted, or it
is not pre-formatted. It would not be hard to break your text into
paragraphs (by splitting on newlines), and then parse each paragraph to
determine what kind of formatting to apply. Either that, or do the
line-wrapping on your own, and write it out as pre-formatted."""
    para = Paragraph(text, style)
    para.wrapOn(p,300,50)
    para.drawOn(p, 200, 200)
    
    draw_para_box(p, "first row is now long enough to see if it will wrap", 0, 0)
    draw_para_box(p, "second row is much longer row that goes on and on and on", 0, 1, 4)
    draw_para_box(p, "third row is much longer row", 0, 2, 2, (1, 1, .50))
    draw_para_box(p, text, 2, 2, 2, (0.5, 1, 0.5))


    # Close the PDF object cleanly, and we're done.
    p.showPage()  # also starts a new page!
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="hello.pdf")
    
    
def render_pdf_list(context):
    # context has title, meta_data and lst
    # 


    buffer = io.BytesIO()
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setPageSize( (height, width) )
    p.setTitle(context['title'])
    #print(p.getAvailableFonts ())




    count = 0
    for col in context['meta_data']:
        if 'no_list' not in col and 'edit_only' not in col:
            size = col['size'] if 'size' in col else 1
            draw_para_box(p, col['heading'], count, 0, size, (0.5, 0.5, 1))
            count += size





    """
    # Table body
    count = 0
    row_classes = ['odd', 'even']
    for row in data:
        html += f'  <tr class={row_classes[count % 2]}>'
        count += 1
        for col in meta_data:
            if 'no_list' not in col:
                html += interpolate('<td>{value}</td>\n', col, row)
    """




    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFillColorRGB(0, 0, 0.5)
    p.setStrokeColorRGB(0.5, 0, 0)
    p.setFont("Times-Roman", 16,leading=None)
    p.drawString(100, 500, "Hello world.")
    p.line(100, 490, 300, 490)


    style = getSampleStyleSheet()["Normal"]

    text = """You can't have it both ways. Either your text is pre-formatted, or it
is not pre-formatted. It would not be hard to break your text into
paragraphs (by splitting on newlines), and then parse each paragraph to
determine what kind of formatting to apply. Either that, or do the
line-wrapping on your own, and write it out as pre-formatted."""
    para = Paragraph(text, style)
    para.wrapOn(p,300,50)
    para.drawOn(p, 200, 200)
    
    #draw_para_box(p, "first row is now long enough to see if it will wrap", 0, 0)
    draw_para_box(p, "second row is much longer row that goes on and on and on", 0, 1, 4)
    draw_para_box(p, "third row is much longer row", 0, 2, 2, (1, 1, .50))
    draw_para_box(p, text, 2, 2, 2, (0.5, 1, 0.5))


    # Close the PDF object cleanly, and we're done.
    p.showPage()  # also starts a new page!






    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="hello.pdf")



def draw_paragraph(canvas, text, x, y, col_count = 1):
    ps = ParagraphStyle('text')
    size = MAX_FONT_SIZE + 1
    h = 999
    while h > (TABLE_ROW_UNIT - 2 * PADDING) and size >= MIN_FONT_SIZE:
        size -= 1
        ps.fontSize = size
        ps.leading = size * 1.2
        para = Paragraph(text, ps)
        w, h = para.wrapOn(canvas, TABLE_COL_UNIT * col_count - 2 * PADDING, TABLE_ROW_UNIT - 2 * PADDING)
    para.drawOn(canvas, LEFT + x * TABLE_COL_UNIT + PADDING, TOP - y * TABLE_ROW_UNIT - PADDING - h)


def draw_para_box(canvas, text, x, y, col_count = 1, colour = None):
    canvas.setStrokeColorRGB(0, 0, 0.5)
    if colour:
        canvas.setFillColorRGB(*colour)
        canvas.rect(LEFT + x * TABLE_COL_UNIT, TOP - (y + 1) * TABLE_ROW_UNIT,  TABLE_COL_UNIT * col_count, TABLE_ROW_UNIT, fill=1)
    else:
        canvas.rect(LEFT + x * TABLE_COL_UNIT, TOP - (y + 1) * TABLE_ROW_UNIT,  TABLE_COL_UNIT * col_count, TABLE_ROW_UNIT, fill=0)
    draw_paragraph(canvas, text, x, y, col_count)



