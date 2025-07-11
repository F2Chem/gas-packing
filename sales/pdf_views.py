import datetime
import io
import re

from django.http import FileResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib import colors
from reportlab.graphics.shapes import *
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from util.util import day_month_year


def create_pdf(obj, title):
    customer = obj.customer
    zone = customer.zone
    nonhazardous = True
    lines = obj.lines()
    print(zone)
    print(lines)
    # need to get lines for obj for various products

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    width, height = A4
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setPageSize( (width, height) )
    p.setTitle(title)
    #print(p.getAvailableFonts ())

    draw_logo(p, 20, 720)
    draw_controlled_shipment(p, 440, 760)
    draw_f2_address(p, 120, 740)
    draw_title(p, nonhazardous)
    draw_header_data(p, obj.created_at, obj.our_ref, obj.customer_ref, customer.invoice_address, customer.delivery_address, 'customer.contact')


    p.showPage()  # also starts a new page!
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="f2-license-" + obj.our_ref + ".pdf")
    

def controlled_shipment(canvas, x_offset, y_offset):
    canvas.setStrokeColorRGB(*_colour_from_hex('000066')) 
    canvas.rect(x_offset, y_offset, 120 * scale, 160 * scale, fill=0, stroke=1)
    


def draw_logo(canvas, x_offset, y_offset):
    scale = 0.6  # If you change the scale, the F and 2 will move relative to the box!
    canvas.setFillColorRGB(*_colour_from_hex('000066')) 
    canvas.rect(x_offset, y_offset, 120 * scale, 160 * scale, fill=1, stroke=0)
    canvas.setFillColorRGB(*_colour_from_hex('4fffa1')) 

    x_offset -= 25
    y_offset += 140
    draw_path(canvas, "M 94.75,99 L 58.1,200 H 85.06 L 100,159 h 21.55 l 8.35,-23 h -21.6 l 5.1,-14 H 135 l 8.35,-23 z", x_offset, y_offset, scale)
    draw_path(canvas, "M 82.000387,210 H 137.6 l 3.65,-10 h -18.29961 l 17.15,-8.5 c 4.0184,-1.99163 6.91026,-4.50756 6.89961,-6.98 c -0.0259,-6.00503 -9.62406,-11.47992 -17.43602,-11.50395 c -13.18942,-0.0406 -19.29736,2.78763 -24.76359,11.98395 h 13.3 c -0.0361,-2.48389 5.25421,-3.98296 8.5,-4 c 2.79433,-0.0147 5.68417,1.1832 5.5,3 c -0.11166,1.1015 -2.62478,2.22762 -4.30253,3.06772 z", x_offset, y_offset, scale)


def _colour_from_hex(s):
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    print(r, g, b)
    return r / 255, g / 255, b / 255

# Assumes the first instruction is an M and z brings us back to that point
def draw_path(canvas, str, x_offset = 100, y_offset = 400, scale = 1.0):
    path = canvas.beginPath()
    sections = re.split(r' (?=[a-zA-Z])', str)
    cursor_x = 0
    cursor_y = 0
    start_x = 0
    start_y = 0
    start_set = False
    for section in sections:
        bits = section.split(' ')
        
        if (bits[0] == 'M'):
            x, y = _to_coord(bits[1])
            cursor_x = x * scale
            cursor_y = y * scale
            path.moveTo(x_offset + cursor_x, y_offset - cursor_y)
            if not start_set:
                start_x = cursor_x
                start_y = cursor_y
                start_set = True                
            
        if (bits[0] == 'm'):
            x, y = _to_coord(bits[1])
            cursor_x += x * scale
            cursor_y += y * scale
            path.moveTo(x_offset + cursor_x, y_offset - cursor_y)
        
        if (bits[0] == 'L'):
            x, y = _to_coord(bits[1])
            cursor_x = x * scale
            cursor_y = y * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'l'):
            x, y = _to_coord(bits[1])
            cursor_x += x * scale
            cursor_y += y * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'H'):
            x = float(bits[1])
            cursor_x = x * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'h'):
            x = float(bits[1])
            cursor_x += x * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'V'):
            y = float(bits[1])
            cursor_y = y * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'v'):
            y = float(bits[1])
            cursor_y += y * scale
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            
        if (bits[0] == 'c'):
            p1 = _to_coord(bits[1])
            p2 = _to_coord(bits[2])
            p3 = _to_coord(bits[3])
            path.curveTo(x_offset + cursor_x  + p1[0] * scale,
                         y_offset - cursor_y  - p1[1] * scale, 
                         x_offset + cursor_x  + p2[0] * scale, 
                         y_offset - cursor_y  - p2[1] * scale, 
                         x_offset + cursor_x  + p3[0] * scale, 
                         y_offset - cursor_y  - p3[1] * scale)
            cursor_x += p3[0] * scale
            cursor_y += p3[1] * scale
            
        if (bits[0] == 'z'):
            cursor_x = start_x
            cursor_y = start_y
            path.lineTo(x_offset + cursor_x, y_offset - cursor_y)
            

    canvas.drawPath(path, fill=1, stroke=0)

def _to_coord(str):
    s = str.split(',')
    return float(s[0]), float(s[1])




def draw_controlled_shipment(canvas, x, y):
    w = 115
    h = 35
    canvas.setStrokeColorRGB(0.8, 0, 0)
    canvas.setFillColorRGB(0.8, 0, 0)
    canvas.setLineWidth(3)
    canvas.rect(x - 5, y - 5,  w + 10, h + 10, stroke=1, fill=0)
    canvas.setLineWidth(1.0)
    canvas.rect(x, y,  w, h, stroke=1, fill=0)
    canvas.drawString(x + 5, y + 20, "CONTROLLED")
    canvas.drawString(x + 20, y + 5, "SHIPMENT")
    canvas.setFillColorRGB(0, 0, 0)
    
    
    
def draw_f2_address(canvas, x, y):
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(x, y + 48, "F2 Chemicals Ltd")
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x, y + 36, "Lea Lane, Lea Town, Preston, PR4 0RZ UK")
    canvas.drawString(x, y + 24, "Tel: +44 (0) 1772 775836")
    canvas.drawString(x, y + 12, "E-mail: Hadassah.winkley@f2chemicals.com")
    canvas.drawString(x, y + 0, "VAT Number: 759 308 793       Company no: 2680159")


def draw_title(canvas, nonhazardous):
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawCentredString(canvas._pagesize[0] / 2, 700, "**** CUSTOMS INVOICE/PACKING LIST ****")

    if nonhazardous:
        canvas.setFillColorRGB(*_colour_from_hex('000066')) 
        canvas.drawCentredString(canvas._pagesize[0] / 2, 686, "*** THESE PRODUCTS ARE NOT TOXIC AND NOT HAZARDOUS ***")
        canvas.setFillColorRGB(0, 0, 0)

def draw_header_data(canvas, date, our_ref, customer_ref, add1, add2, customer):
    canvas.setFont('Helvetica-BoldOblique', 10)
    canvas.drawString(20, 615, "Invoice Address")
    canvas.drawString(220, 615, "Delivery Address")

    canvas.setFont('Helvetica', 10)
    canvas.drawString(20, 660, day_month_year(date))
    canvas.drawString(220, 660, 'Our ref: ' + our_ref)
    canvas.drawString(420, 660, 'PO number: ' + customer_ref)
    draw_address(canvas, add1, 20, 600)
    draw_address(canvas, add2, 220, 600)
    canvas.drawString(20, 645, 'Contact: ' + customer.contact_name)
    canvas.drawString(220, 645, 'Phone: ' + customer.contact_phone)
    canvas.drawString(420, 645, 'e-Mail: ' + customer.contact_email)



def draw_address(canvas, text, x, y):
    for i, line in enumerate(text.split('\n')):
        canvas.drawString(x, y - i * 12, line.strip())
