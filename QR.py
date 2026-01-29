import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Reflective Windshield QR", layout="centered")
st.title("🚘 Reflective Vehicle Windshield QR (PDF Generator)")

# ---------------- INPUTS ----------------
st.subheader("QR Details")

qr_mode = st.radio("QR Source", ["Generate from Links", "Upload QR Images"])
qr_imgs = []

if qr_mode == "Generate from Links":
    links = st.text_area(
        "Paste QR links (one per line)",
        placeholder="https://example1.com\nhttps://example2.com"
    )
    if links:
        for link in links.splitlines():
            if link.strip():
                qr_imgs.append(qrcode.make(link.strip()).convert("RGB"))
else:
    uploaded_qrs = st.file_uploader(
        "Upload QR Images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    if uploaded_qrs:
        for f in uploaded_qrs:
            qr_imgs.append(Image.open(f).convert("RGB"))

# ---------------- COMPANY INFO ----------------
st.subheader("Company Info")
company_email = st.text_input("Company Email", "info@company.com")
company_url = st.text_input("Company Website", "www.meripahchan.in")
insta_id = st.text_input("Instagram ID", "@meripahchanindia")

# ---------------- PROCESS ----------------
if qr_imgs:
    LOGO_FILE = "static_logo.png"
    if not os.path.exists(LOGO_FILE):
        st.error("❌ static_logo.png not found")
        st.stop()

    logo_img = Image.open(LOGO_FILE).convert("RGBA")

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # ---------- CARD SIZE (8cm x 10cm) ----------
    CM = 28.35
    CARD_W = 8 * CM
    CARD_H = 10 * CM
    GAP = 20

    START_X = 40
    y = [A4[1] - CARD_H - 40]

    def draw_card(qr_img):
        cx = START_X + CARD_W / 2

        # ---- BACKGROUND (Premium Light Grey) ----
        c.setFillColorRGB(0.96, 0.97, 0.98)
        c.roundRect(START_X, y[0], CARD_W, CARD_H, 14, fill=1, stroke=0)

        # ---- BORDER ----
        c.setStrokeColorRGB(0.1, 0.1, 0.1)
        c.setLineWidth(2)
        c.roundRect(START_X + 3, y[0] + 3, CARD_W - 6, CARD_H - 6, 12)

        # ---- LOGO (TOP CENTER) ----
        c.drawImage(
            ImageReader(logo_img),
            cx - 60,
            y[0] + CARD_H - 45,
            130,
            30,

            mask="auto"
        )

        # ---- QR (CENTER MAIN) ----
        qr_size = 138
        qr_x = cx - qr_size / 2
        qr_y = y[0] + CARD_H - 200

        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)

        c.setStrokeColorRGB(0.15, 0.15, 0.15)
        c.setLineWidth(1.6)
        c.rect(qr_x - 8, qr_y - 8, qr_size + 16, qr_size + 16)

        c.drawImage(ImageReader(buf), qr_x, qr_y, qr_size, qr_size)

        # ---- SCAN TEXT (BELOW QR – FIXED) ----
        c.setFillColorRGB(0.05, 0.1, 0.2)
        c.setFont("Helvetica-Bold", 15)
        c.drawCentredString(
            cx,
            qr_y - 25,
            "SCAN TO CONTACT OWNER"
        )

        # ---- DIVIDER ----
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.line(
            START_X + 30,
            y[0] + 78,
            START_X + CARD_W - 30,
            y[0] + 78
        )

        # ---- CONTACT DETAILS WITH ICONS ----
        c.setFont("Helvetica", 9.5)
        c.setFillColorRGB(0, 0, 0)

        c.drawCentredString(cx, y[0] + 40, f"url:  : {company_url}")
        c.drawCentredString(cx, y[0] + 25, f" ✉ Email     : {company_email}")
        c.drawCentredString(cx, y[0] + 12, f"📸 Instagram : {insta_id}")
        # ---- NEXT CARD ----
        y[0] -= (CARD_H + GAP)
        if y[0] < 60:
            c.showPage()
            y[0] = A4[1] - CARD_H - 40

    for img in qr_imgs:
        draw_card(img)

    c.save()
    pdf_buffer.seek(0)

    st.success("✅ Professional 8×10cm QR Card Generated (No Overlap)")

    st.download_button(
        "⬇ Download PDF",
        data=pdf_buffer,
        file_name="vehicle_qr_8x10cm_professional.pdf",
        mime="application/pdf"
    )

else:
    st.info("👉 Add QR links or upload QR images to continue.")
