import streamlit as st
import pandas as pd
import json
import os

from dotenv import load_dotenv
load_dotenv()

from crewai import Crew

from tools import OCRTool
from tasks import create_bill_task


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Bill Extractor",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 AI Multi-Bill Extraction System")

st.write(
    "Upload one or multiple bills and extract structured data automatically."
)


# ==========================================
# CREATE FOLDERS
# ==========================================

os.makedirs("bills", exist_ok=True)
os.makedirs("extracted_data", exist_ok=True)


# ==========================================
# FILE UPLOADER
# ==========================================

uploaded_files = st.file_uploader(
    "Upload Bill Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)


# ==========================================
# OCR INIT
# ==========================================

ocr = OCRTool()


# ==========================================
# PROCESS FILES
# ==========================================

if uploaded_files:

    all_summary_data = []

    for uploaded_file in uploaded_files:

        st.divider()

        st.header(f"📄 Processing: {uploaded_file.name}")

        # ==========================================
        # SAVE IMAGE
        # ==========================================

        file_path = os.path.join(
            "bills",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # ==========================================
        # OCR + AI
        # ==========================================

        with st.spinner(
            f"Extracting {uploaded_file.name}..."
        ):

            # OCR
            bill_text = ocr.extract_text(
                file_path
            )

            # DEBUG OCR
            with st.expander("DEBUG OCR TEXT"):

                st.text(bill_text)

            # TASK
            task = create_bill_task(
                bill_text
            )

            # CREW
            crew = Crew(
                agents=[task.agent],
                tasks=[task],
                verbose=False
            )

            # RUN AI
            result = crew.kickoff()

            # DEBUG AI
            with st.expander("DEBUG AI OUTPUT"):

                st.write(result)

        # ==========================================
        # CLEAN AI OUTPUT
        # ==========================================

        try:

            result_str = str(result).strip()

            result_str = result_str.replace(
                "```json",
                ""
            )

            result_str = result_str.replace(
                "```",
                ""
            )

            try:

                bill_data = json.loads(
                    result_str
                )

            except:

                st.error(
                    "AI returned invalid JSON"
                )

                st.text(result_str)

                st.stop()

            st.success(
                f"{uploaded_file.name} processed successfully ✅"
            )

            # ==========================================
            # SHOP DETAILS
            # ==========================================

            st.subheader("🏪 Shop Details")

            shop_df = pd.DataFrame([{

                "Shop Name":
                bill_data.get("shop_name"),

                "Address":
                bill_data.get("address"),

                "Phone":
                bill_data.get("phone"),

                "GST Number":
                bill_data.get("gst_number"),

                "Date":
                bill_data.get("date"),

                "Payment Method":
                bill_data.get("payment_method")

            }])

            st.table(shop_df)

            # ==========================================
            # ITEMS TABLE
            # ==========================================

            st.subheader("🛒 Purchased Items")

            items = bill_data.get(
                "items",
                []
            )

            if isinstance(items, list):

                items_df = pd.DataFrame(items)

            else:

                items_df = pd.DataFrame()

            if not items_df.empty:

                st.dataframe(
                    items_df,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No items detected."
                )

            # ==========================================
            # BILL SUMMARY
            # ==========================================

            st.subheader("💰 Bill Summary")

            summary_df = pd.DataFrame([{

                "Subtotal":
                bill_data.get("subtotal"),

                "Tax":
                bill_data.get("tax"),

                "Total":
                bill_data.get("total")

            }])

            st.table(summary_df)

            # ==========================================
            # SAVE JSON
            # ==========================================

            json_path = os.path.join(
                "extracted_data",
                f"{uploaded_file.name}.json"
            )

            with open(
                json_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    bill_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            # ==========================================
            # SAVE CSV
            # ==========================================

            csv_path = os.path.join(
                "extracted_data",
                f"{uploaded_file.name}.csv"
            )

            items_df.to_csv(
                csv_path,
                index=False
            )

            # ==========================================
            # DOWNLOAD BUTTONS
            # ==========================================

            st.subheader(
                "⬇ Download Structured Data"
            )

            col1, col2 = st.columns(2)

            # JSON DOWNLOAD
            with col1:

                with open(json_path, "rb") as f:

                    st.download_button(
                        label=f"Download JSON - {uploaded_file.name}",
                        data=f,
                        file_name=f"{uploaded_file.name}.json",
                        mime="application/json"
                    )

            # CSV DOWNLOAD
            with col2:

                with open(csv_path, "rb") as f:

                    st.download_button(
                        label=f"Download CSV - {uploaded_file.name}",
                        data=f,
                        file_name=f"{uploaded_file.name}.csv",
                        mime="text/csv"
                    )

            # ==========================================
            # SUMMARY DATA
            # ==========================================

            all_summary_data.append({

                "File":
                uploaded_file.name,

                "Shop Name":
                bill_data.get("shop_name"),

                "Date":
                bill_data.get("date"),

                "Total":
                bill_data.get("total"),

                "Payment Method":
                bill_data.get("payment_method")

            })

        except Exception as e:

            st.error(
                f"Failed to process {uploaded_file.name}"
            )

            st.exception(e)

    # ==========================================
    # MASTER DASHBOARD
    # ==========================================

    if all_summary_data:

        st.divider()

        st.header(
            "📊 All Bills Summary"
        )

        final_summary_df = pd.DataFrame(
            all_summary_data
        )

        st.dataframe(
            final_summary_df,
            use_container_width=True
        )

        # ==========================================
        # SAVE MASTER CSV
        # ==========================================

        master_csv_path = os.path.join(
            "extracted_data",
            "all_bills_summary.csv"
        )

        final_summary_df.to_csv(
            master_csv_path,
            index=False
        )

        # ==========================================
        # DOWNLOAD MASTER CSV
        # ==========================================

        with open(master_csv_path, "rb") as f:

            st.download_button(
                label="⬇ Download All Bills Summary CSV",
                data=f,
                file_name="all_bills_summary.csv",
                mime="text/csv"
            )