import easyocr
import re


class OCRTool:

    def __init__(self):

        self.reader = easyocr.Reader(['en'])

    def extract_bill_data(self, image_path):

        result = self.reader.readtext(
            image_path,
            detail=0,
            paragraph=True
        )

        text = "\n".join(result)

        lines = text.split("\n")

        # SHOP NAME
        shop_name = lines[0] if lines else ""

        # ADDRESS
        address = " ".join(lines[1:3])

        # TOTAL
        total = ""

        for line in reversed(lines):

            if "total" in line.lower():

                numbers = re.findall(
                    r"\d+[.,]?\d*",
                    line
                )

                if numbers:

                    total = numbers[-1]
                    break

        return {

            "shop_name": shop_name,
            "address": address,
            "total": total,
            "raw_text": text,
            "items": lines[3:-3]

        }