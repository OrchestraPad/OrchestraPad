from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Dies ist ein Test-Notenblatt!", ln=1, align="C")
pdf.output("usb_drive/Test_Song.pdf")
