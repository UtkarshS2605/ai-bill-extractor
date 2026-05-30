import easyocr


class OCRTool:

    def __init__(self):

        # English + Hindi/Marathi
        self.reader = easyocr.Reader(
            ['en', 'hi']
        )

    def extract_text(self, image_path):

        result = self.reader.readtext(
            image_path,
            detail=0,
            paragraph=True
        )

        return "\n".join(result)