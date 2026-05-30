from crewai import Task
from agents import bill_agent


def create_bill_task(text):

    return Task(

        description=f"""
        Extract structured bill data
        from this OCR text.

        IMPORTANT:
        - Return ONLY valid JSON
        - Do NOT add explanations
        - Do NOT add markdown
        - Do NOT write notes
        - Return pure JSON only

        Items MUST be array format.

        Example:

        "items": [
          {{
            "name": "Milk",
            "quantity": "2",
            "price": "40"
          }}
        ]

        OCR TEXT:
        ----------------

        {text}
        """,

        expected_output="""
        {
            "shop_name":"",
            "address":"",
            "phone":"",
            "gst_number":"",
            "date":"",
            "items":[],
            "subtotal":"",
            "tax":"",
            "total":"",
            "payment_method":""
        }
        """,

        agent=bill_agent
    )