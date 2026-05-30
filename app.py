import streamlit as st
import pandas as pd
import os

from tools import OCRTool


st.set_page_config(
    page_title="AI Bill Extractor",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 AI Bill Extractor")


os.makedirs("bills", exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload Bills",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

ocr = OCRTool()

if uploaded_files:

    for uploaded_file in uploaded_files:

        st.divider()

        st.header(uploaded_file.name)

        file_path = os.path.join(
            "bills",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:

            f.write(
                uploaded_file.getbuffer()
            )

        with st.spinner("Processing..."):

            bill_data = ocr.extract_bill_data(
                file_path
            )

        st.subheader("Shop Details")

        shop_df = pd.DataFrame([{

            "Shop Name":
            bill_data["shop_name"],

            "Address":
            bill_data["address"],

            "Total":
            bill_data["total"]

        }])

        st.table(shop_df)

        st.subheader("Detected Lines")

        items_df = pd.DataFrame({

            "Text":
            bill_data["items"]

        })

        st.dataframe(
            items_df,
            use_container_width=True
        )

        with st.expander("Raw OCR Text"):

            st.text(
                bill_data["raw_text"]
            )