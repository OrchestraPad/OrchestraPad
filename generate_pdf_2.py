from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Ein zweites Lied (Song 2)", ln=1, align="C")
pdf.output("usb_drive/Song_2.pdf")
