from typing import TypedDict, List
from langchain_core.documents import Document


class AgentState(TypedDict):
    claim_id: str
    patient_name: str
    policy_number: str
    diagnosis: str
    treatment: str

    retrieved_documents: List[Document]

    coverage_result: dict
    waiting_period_result: dict
    exclusion_result: dict
    fraud_result: dict

    final_decision: str
    report: str