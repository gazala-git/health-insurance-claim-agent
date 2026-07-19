import pandas as pd
import streamlit as st


from src.graph import graph


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Health Insurance Claim Adjudication Agent",
    page_icon="🏥",
    layout="wide"
)


# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULTS = {
    "patient_name": "",
    "claim_id": "",
    "policy_number": "",
    "diagnosis": "",
    "treatment": "",
    "result": None,
    "form_version": 0
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def reset_form():
    """
    Completely reset the claim form.
    """

    st.session_state.patient_name = ""
    st.session_state.claim_id = ""
    st.session_state.policy_number = ""
    st.session_state.diagnosis = ""
    st.session_state.treatment = ""

    st.session_state.result = None

    # Create fresh widgets
    st.session_state.form_version += 1
    # ==========================================================
# HEADER
# ==========================================================

left, right = st.columns([8, 1])

with left:

    st.title("🏥 Health Insurance Claim Adjudication Agent")

    st.caption(
        "AI Powered Health Insurance Claim Assessment using LangGraph + RAG"
    )

with right:

    st.write("")
    st.write("")

    if st.button(
        "🆕 New Claim",
        use_container_width=True
    ):

        reset_form()
        st.rerun()

st.divider()

# ==========================================================
# CLAIM FORM
# ==========================================================

st.subheader("📝 Claim Details")

with st.form(f"claim_form_{st.session_state.form_version}"):

    left, right = st.columns(2)

    with left:

        patient_name = st.text_input(
            "Patient Name",
            value=st.session_state.patient_name,
            key=f"patient_name_{st.session_state.form_version}"
        )

        claim_id = st.text_input(
            "Claim ID",
            value=st.session_state.claim_id,
            key=f"claim_id_{st.session_state.form_version}"
        )

        diagnosis = st.text_area(
            "Diagnosis",
            value=st.session_state.diagnosis,
            height=120,
            key=f"diagnosis_{st.session_state.form_version}"
        )

    with right:

        policy_number = st.text_input(
            "Policy Number",
            value=st.session_state.policy_number,
            key=f"policy_number_{st.session_state.form_version}"
        )

        treatment = st.text_area(
            "Treatment",
            value=st.session_state.treatment,
            height=120,
            key=f"treatment_{st.session_state.form_version}"
        )

    submitted = st.form_submit_button(
        "✅ Evaluate Claim",
        use_container_width=True
    )

# ==========================================================
# RUN GRAPH
# ==========================================================

if submitted:

    if not all([
        patient_name.strip(),
        claim_id.strip(),
        policy_number.strip(),
        diagnosis.strip(),
        treatment.strip()
    ]):

        st.error("Please fill in all the fields before evaluating the claim.")

    else:

        st.session_state.patient_name = patient_name
        st.session_state.claim_id = claim_id
        st.session_state.policy_number = policy_number
        st.session_state.diagnosis = diagnosis
        st.session_state.treatment = treatment

        initial_state = {

            "claim_id": claim_id,

            "patient_name": patient_name,

            "policy_number": policy_number,

            "diagnosis": diagnosis,

            "treatment": treatment,

            "retrieved_documents": [],

            "coverage_result": {},

            "waiting_period_result": {},

            "exclusion_result": {},

            "fraud_result": {},

            "final_decision": {},

            "report": ""

        }

        try:

            with st.spinner("🔍 Analysing Insurance Policy..."):

                result = graph.invoke(initial_state)

            st.session_state.result = result

        except Exception as e:

            st.error(f"Error while evaluating claim:\n\n{e}")
# ==========================================================
# SHOW REPORT
# ==========================================================

if st.session_state.result:

    result = st.session_state.result

    st.success("✅ Claim Evaluation Completed Successfully")

    # ==========================================================
    # CLAIM INFORMATION
    # ==========================================================

    st.markdown("## 📋 Claim Information")

    claim_df = pd.DataFrame(
        [
            ["Claim ID", result["claim_id"]],
            ["Patient Name", result["patient_name"]],
            ["Policy Number", result["policy_number"]],
            ["Diagnosis", result["diagnosis"]],
            ["Treatment", result["treatment"]],
        ],
        columns=["Field", "Value"]
    )

    st.dataframe(
        claim_df,
        use_container_width=True,
        hide_index=True
    )

    st.write("")

    # ==========================================================
    # CLAIM EVALUATION
    # ==========================================================

    st.markdown("## 🔍 Claim Evaluation")

    evaluation_df = pd.DataFrame(
        [
            [
                "Coverage",
                result["coverage_result"]["status"],
                result["coverage_result"]["reason"],
                result["coverage_result"]["evidence"],
            ],
            [
                "Waiting Period",
                result["waiting_period_result"]["status"],
                result["waiting_period_result"]["reason"],
                result["waiting_period_result"]["evidence"],
            ],
            [
                "Exclusion",
                result["exclusion_result"]["status"],
                result["exclusion_result"]["reason"],
                result["exclusion_result"]["evidence"],
            ],
            [
                "Fraud",
                result["fraud_result"]["status"],
                result["fraud_result"]["reason"],
                result["fraud_result"]["evidence"],
            ]
        ],
        columns=[
            "Check",
            "Status",
            "Reason",
            "Policy Evidence"
        ]
    )

    st.dataframe(
        evaluation_df,
        use_container_width=True,
        hide_index=True
    )

    st.write("")

    # ==========================================================
    # FINAL DECISION
    # ==========================================================

    st.markdown("## 🏆 Final Decision")

    decision_df = pd.DataFrame(
        [
            [
                result["final_decision"]["decision"],
                result["final_decision"]["reason"]
            ]
        ],
        columns=[
            "Decision",
            "Reason"
        ]
    )

    st.dataframe(
        decision_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==========================================================
    # PDF REPORT
    # ==========================================================

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "<b>HEALTH INSURANCE CLAIM REPORT</b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph("<b>Claim Information</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(f"Claim ID : {result['claim_id']}", styles["BodyText"])
    )

    story.append(
        Paragraph(f"Patient Name : {result['patient_name']}", styles["BodyText"])
    )

    story.append(
        Paragraph(f"Policy Number : {result['policy_number']}", styles["BodyText"])
    )

    story.append(
        Paragraph(f"Diagnosis : {result['diagnosis']}", styles["BodyText"])
    )

    story.append(
        Paragraph(f"Treatment : {result['treatment']}", styles["BodyText"])
    )

    story.append(Spacer(1, 20))

    sections = [
        ("Coverage Analysis", result["coverage_result"]),
        ("Waiting Period Analysis", result["waiting_period_result"]),
        ("Exclusion Analysis", result["exclusion_result"]),
        ("Fraud Analysis", result["fraud_result"])
    ]

    for title, section in sections:

        story.append(
            Paragraph(f"<b>{title}</b>", styles["Heading2"])
        )

        story.append(
            Paragraph(
                f"<b>Status:</b> {section['status']}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Reason:</b> {section['reason']}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Policy Evidence:</b> {section['evidence']}",
                styles["BodyText"]
            )
        )

        story.append(Spacer(1, 15))

    story.append(
        Paragraph("<b>Final Decision</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(
            f"<b>Decision:</b> {result['final_decision']['decision']}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Reason:</b> {result['final_decision']['reason']}",
            styles["BodyText"]
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()


    # ==========================================================
    # CLAIM SUMMARY
    # ==========================================================

    st.markdown("## 📊 Claim Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Coverage",
            result["coverage_result"]["status"]
        )

    with col2:
        st.metric(
            "Waiting Period",
            result["waiting_period_result"]["status"]
        )

    with col3:
        st.metric(
            "Exclusion",
            result["exclusion_result"]["status"]
        )

    with col4:
        st.metric(
            "Fraud",
            result["fraud_result"]["status"]
        )

    st.divider()

    decision = result["final_decision"]["decision"].lower()

    if decision == "approved":

        st.success(
            f"✅ CLAIM APPROVED\n\n{result['final_decision']['reason']}"
        )

    elif decision == "rejected":

        st.error(
            f"❌ CLAIM REJECTED\n\n{result['final_decision']['reason']}"
        )

    else:

        st.warning(
            f"⏳ CLAIM PENDING\n\n{result['final_decision']['reason']}"
        )
Displaying app.py.
