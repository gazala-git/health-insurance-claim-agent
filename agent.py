import json
import re

from langchain_core.messages import HumanMessage

from src.state import AgentState
from src.utils import vector_db, llm


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def extract_json(text: str) -> str:
    """
    Extract the first JSON object from the LLM response.
    Handles responses that contain extra text before/after JSON.
    """

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(
            f"No JSON object found in LLM response:\n\n{text}"
        )

    return match.group(0)


def clean_llm_response(response):

    """
    Normalize LLM response into plain text.

    Supports:
    - response.content as string
    - response.content as list
    """

    content = response.content

    # -------------------------------
    # String response
    # -------------------------------

    if isinstance(content, str):

        text = content

    # -------------------------------
    # List response
    # -------------------------------

    elif isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict):

                parts.append(item.get("text", ""))

            else:

                parts.append(str(item))

        text = "\n".join(parts)

    else:

        text = str(content)

    # -------------------------------
    # Remove markdown fences
    # -------------------------------

    text = (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )

    return text


# ==========================================================
# POLICY RETRIEVER
# ==========================================================

def policy_retriever(state: AgentState):

    query = f"""
Diagnosis:
{state["diagnosis"]}

Treatment:
{state["treatment"]}
"""

    docs = vector_db.max_marginal_relevance_search(

        query=query,

        k=3,

        fetch_k=10

    )

    print("=" * 80)
    print("Retrieved Documents :", len(docs))
    print("=" * 80)

    for i, doc in enumerate(docs, start=1):

        print(f"\nDocument {i}")

        print("-" * 80)

        print(doc.page_content[:700])

    state["retrieved_documents"] = docs

    return state

# ==========================================================
# CLAIM ANALYZER
# ==========================================================

def claim_analyzer(state: AgentState):

    handbook = "\n\n".join(
        doc.page_content
        for doc in state["retrieved_documents"]
    )

    prompt = f"""
You are a Senior Health Insurance Claims Officer.

Your task is to evaluate the insurance claim STRICTLY using the retrieved
insurance handbook provided below.

Never use outside knowledge.

If the handbook does not contain sufficient information,
explicitly mention that.

==================================================
CLAIM DETAILS
==================================================

Claim ID:
{state["claim_id"]}

Patient Name:
{state["patient_name"]}

Policy Number:
{state["policy_number"]}

Diagnosis:
{state["diagnosis"]}

Treatment:
{state["treatment"]}

==================================================
RETRIEVED INSURANCE HANDBOOK
==================================================

{handbook}

==================================================
TASK
==================================================

Perform ALL of the following analyses.

1. Coverage Analysis

2. Waiting Period Analysis

3. Exclusion Analysis

4. Fraud Analysis

5. Final Decision

==================================================
RULES
==================================================

For EACH analysis provide:

• status

• reason

• evidence

Evidence MUST come ONLY from the retrieved handbook.

If evidence cannot be found, write exactly:

Information not available in retrieved handbook.

If no waiting period exists, write:

The retrieved policy does not indicate that this treatment is subject to a waiting period.

If no exclusion exists, write:

The treatment does not match any exclusion listed in the retrieved policy.

If fraud is not suspected, clearly explain why.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do NOT return Markdown.

Do NOT wrap the JSON inside ```json.

Do NOT write explanations before or after the JSON.

Use EXACTLY the following structure.

{{
    "coverage_result": {{
        "status": "",
        "reason": "",
        "evidence": ""
    }},

    "waiting_period_result": {{
        "status": "",
        "reason": "",
        "evidence": ""
    }},

    "exclusion_result": {{
        "status": "",
        "reason": "",
        "evidence": ""
    }},

    "fraud_result": {{
        "status": "",
        "reason": "",
        "evidence": ""
    }},

    "final_decision": {{
        "decision": "",
        "reason": ""
    }}
}}
"""   
    # ==========================================================
    # INVOKE LLM
    # ==========================================================

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    # ==========================================================
    # CLEAN RESPONSE
    # ==========================================================

    content = clean_llm_response(response)

    print("=" * 80)
    print("RAW LLM RESPONSE")
    print("=" * 80)
    print(content)

    # ==========================================================
    # EXTRACT JSON
    # ==========================================================

    try:

        json_text = extract_json(content)

    except Exception as e:

        raise ValueError(

            "LLM did not return a valid JSON object.\n\n"
            f"Raw Response:\n\n{content}"

        ) from e

    # ==========================================================
    # PARSE JSON
    # ==========================================================

    try:

        result = json.loads(json_text)

    except json.JSONDecodeError as e:

        print("=" * 80)
        print("INVALID JSON")
        print("=" * 80)
        print(json_text)

        raise ValueError(

            "LLM returned malformed JSON.\n\n"
            f"{json_text}"

        ) from e

    print("=" * 80)
    print("JSON PARSED SUCCESSFULLY")
    print("=" * 80)

    # ==========================================================
    # NORMALIZATION FUNCTIONS
    # ==========================================================

    def normalize_section(section, default_status="Unknown"):
        """
        Ensure every analysis section always contains:
        status, reason, evidence
        """

        if not isinstance(section, dict):
            section = {}

        return {
            "status": str(
                section.get("status", default_status)
            ).strip(),

            "reason": str(
                section.get(
                    "reason",
                    "Information not available."
                )
            ).strip(),

            "evidence": str(
                section.get(
                    "evidence",
                    "Information not available in retrieved handbook."
                )
            ).strip()
        }


    def normalize_final_decision(decision):
        """
        Ensure final decision always contains:
        decision, reason
        """

        if not isinstance(decision, dict):
            decision = {}

        return {

            "decision": str(
                decision.get(
                    "decision",
                    "Pending"
                )
            ).strip(),

            "reason": str(
                decision.get(
                    "reason",
                    "Reason not available."
                )
            ).strip()
        }

    # ==========================================================
    # NORMALIZE ALL RESULTS
    # ==========================================================

    coverage = normalize_section(
        result.get("coverage_result"),
        "Unknown"
    )

    waiting = normalize_section(
        result.get("waiting_period_result"),
        "Unknown"
    )

    exclusion = normalize_section(
        result.get("exclusion_result"),
        "Unknown"
    )

    fraud = normalize_section(
        result.get("fraud_result"),
        "Unknown"
    )

    final_decision = normalize_final_decision(
        result.get("final_decision")
    )

    # ==========================================================
    # SAVE RESULTS TO STATE
    # ==========================================================

    state["coverage_result"] = coverage

    state["waiting_period_result"] = waiting

    state["exclusion_result"] = exclusion

    state["fraud_result"] = fraud

    state["final_decision"] = final_decision

    return state

# ==========================================================
# REPORT GENERATOR
# ==========================================================

def report_generator(state: AgentState):

    report = f"""
============================================================
            HEALTH INSURANCE CLAIM REPORT
============================================================

CLAIM INFORMATION
------------------------------------------------------------

Claim ID       : {state.get("claim_id", "")}

Patient Name   : {state.get("patient_name", "")}

Policy Number  : {state.get("policy_number", "")}

Diagnosis      : {state.get("diagnosis", "")}

Treatment      : {state.get("treatment", "")}

============================================================
CLAIM EVALUATION
============================================================

1. COVERAGE ANALYSIS
------------------------------------------------------------

Status
------
{state["coverage_result"]["status"]}

Reason
------
{state["coverage_result"]["reason"]}

Policy Evidence
---------------
{state["coverage_result"]["evidence"]}


============================================================

2. WAITING PERIOD ANALYSIS
------------------------------------------------------------

Status
------
{state["waiting_period_result"]["status"]}

Reason
------
{state["waiting_period_result"]["reason"]}

Policy Evidence
---------------
{state["waiting_period_result"]["evidence"]}


============================================================

3. EXCLUSION ANALYSIS
------------------------------------------------------------

Status
------
{state["exclusion_result"]["status"]}

Reason
------
{state["exclusion_result"]["reason"]}

Policy Evidence
---------------
{state["exclusion_result"]["evidence"]}


============================================================

4. FRAUD ANALYSIS
------------------------------------------------------------

Status
------
{state["fraud_result"]["status"]}

Reason
------
{state["fraud_result"]["reason"]}

Policy Evidence
---------------
{state["fraud_result"]["evidence"]}


============================================================
FINAL DECISION
============================================================

Decision
--------
{state["final_decision"]["decision"]}

Reason
------
{state["final_decision"]["reason"]}

============================================================
"""

    state["report"] = report

    return state