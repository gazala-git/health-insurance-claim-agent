from fpdf import FPDF
import streamlit as st
from src.graph import graph

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Health Insurance Claim Adjudication Agent",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------------------------------
# Initialize Session State
# ---------------------------------------------------
defaults = {
    "patient_name": "",
    "claim_id": "",
    "policy_number": "",
    "diagnosis": "",
    "treatment": "",
    "report": None,
    "result": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------
# Header
# ---------------------------------------------------
col1, col2 = st.columns([6, 1])

with col1:
    st.title("🏥 Health Insurance Claim Adjudication Agent")

with col2:
    st.write("")
    st.write("")
    if st.button("🆕 New Claim", use_container_width=True):
        for key in defaults.keys():
            st.session_state[key] = defaults[key]
        st.rerun()

st.write(
    "Enter the patient and claim details below to evaluate the insurance claim."
)

# ---------------------------------------------------
# Input Form
# ---------------------------------------------------
with st.form("claim_form"):

    patient_name = st.text_input(
        "Patient Name",
        key="patient_name"
    )

    claim_id = st.text_input(
        "Claim ID",
        key="claim_id"
    )

    policy_number = st.text_input(
        "Policy Number",
        key="policy_number"
    )

    diagnosis = st.text_area(
        "Diagnosis",
        key="diagnosis"
    )

    treatment = st.text_area(
        "Treatment",
        key="treatment"
    )

    submitted = st.form_submit_button(
        "✅ Evaluate Claim",
        use_container_width=True
    )

# ---------------------------------------------------
# Run Agent
# ---------------------------------------------------
if submitted:

    initial_state = {
        "claim_id": claim_id,
        "patient_name": patient_name,
        "policy_number": policy_number,
        "diagnosis": diagnosis,
        "treatment": treatment,
        "retrieved_documents": "",
        "coverage_result": "",
        "waiting_period_result": "",
        "exclusion_result": "",
        "fraud_result": "",
        "final_decision": "",
        "report": ""
    }

    with st.spinner("Evaluating claim..."):
        result = graph.invoke(initial_state)

    # Store the complete result for UI rendering
    st.session_state.result = result
    st.session_state.report = result["report"]

# ---------------------------------------------------
# Report
# ---------------------------------------------------
if st.session_state.result:

    result = st.session_state.result

    st.success("✅ Claim evaluation completed!")

    # -------------------------------
    # Claim Summary
    # -------------------------------
    st.subheader("Claim Summary")

    summary_rows = [
        {"Field": "Patient Name", "Value": result["patient_name"]},
        {"Field": "Claim ID", "Value": result["claim_id"]},
        {"Field": "Policy Number", "Value": result["policy_number"]},
        {"Field": "Diagnosis", "Value": result["diagnosis"]},
        {"Field": "Treatment", "Value": result["treatment"]},
    ]

    st.table(summary_rows)

    st.divider()

    # -------------------------------
    # Coverage Analysis
    # -------------------------------
    st.subheader("Coverage Analysis")

    st.table([
        {"Field": "Status", "Value": result["coverage_result"]["status"]},
        {"Field": "Reason", "Value": result["coverage_result"]["reason"]},
        {"Field": "Policy Evidence", "Value": result["coverage_result"]["evidence"]},
    ])

    st.divider()

    # -------------------------------
    # Waiting Period Analysis
    # -------------------------------
    st.subheader("Waiting Period Analysis")

    st.table([
        {"Field": "Status", "Value": result["waiting_period_result"]["status"]},
        {"Field": "Reason", "Value": result["waiting_period_result"]["reason"]},
        {"Field": "Policy Evidence", "Value": result["waiting_period_result"]["evidence"]},
    ])

    st.divider()

    # -------------------------------
    # Exclusion Analysis
    # -------------------------------
    st.subheader("Exclusion Analysis")

    st.table([
        {"Field": "Status", "Value": result["exclusion_result"]["status"]},
        {"Field": "Reason", "Value": result["exclusion_result"]["reason"]},
        {"Field": "Policy Evidence", "Value": result["exclusion_result"]["evidence"]},
    ])

    st.divider()

    # -------------------------------
    # Fraud Analysis
    # -------------------------------
    st.subheader("Fraud Analysis")

    st.table([
        {"Field": "Status", "Value": result["fraud_result"]["status"]},
        {"Field": "Reason", "Value": result["fraud_result"]["reason"]},
        {"Field": "Policy Evidence", "Value": result["fraud_result"]["evidence"]},
    ])

    st.divider()

    # -------------------------------
    # Final Decision
    # -------------------------------
    st.subheader("Final Decision")

    st.table([
        {"Field": "Decision", "Value": result["final_decision"]["decision"]},
        {"Field": "Reason", "Value": result["final_decision"]["reason"]},
    ])



# ---------------------------------------------------
# Download PDF
# ---------------------------------------------------
if st.session_state.result:

    result = st.session_state.result

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    page_width = pdf.w - 20

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(page_width, 10, "Health Insurance Claim Report", ln=True, align="C")
    pdf.ln(8)

    # Claim Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(page_width, 10, "Claim Summary", ln=True)

    pdf.set_font("Arial", "", 11)

    summary = [
        ("Patient Name", result["patient_name"]),
        ("Claim ID", result["claim_id"]),
        ("Policy Number", result["policy_number"]),
        ("Diagnosis", result["diagnosis"]),
        ("Treatment", result["treatment"]),
    ]

    for field, value in summary:
        pdf.multi_cell(page_width, 8, f"{field}: {value}")

    pdf.ln(5)

    def add_section(title, data):
        pdf.set_font("Arial", "B", 13)
        pdf.cell(page_width, 8, title, ln=True)

        pdf.set_font("Arial", "", 11)

        for key, value in data.items():
            label = key.replace("_", " ").title()
            pdf.multi_cell(page_width, 8, f"{label}: {value}")

        pdf.ln(4)

    add_section("Coverage Analysis", result["coverage_result"])
    add_section("Waiting Period Analysis", result["waiting_period_result"])
    add_section("Exclusion Analysis", result["exclusion_result"])
    add_section("Fraud Analysis", result["fraud_result"])
    add_section("Final Decision", result["final_decision"])

    try:
        pdf_bytes = bytes(pdf.output(dest="S"))
    except TypeError:
        pdf_bytes = pdf.output(dest="S").encode("latin-1")

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name=f"claim_report_{result['claim_id']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
