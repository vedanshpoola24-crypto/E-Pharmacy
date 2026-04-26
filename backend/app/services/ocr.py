def extract_text_from_file(path):
    try:
        import pytesseract
        from PIL import Image

        if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception:
        pass
    return "OCR queued. Install Tesseract and pytesseract for automatic extraction."
