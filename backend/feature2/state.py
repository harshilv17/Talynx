from typing import TypedDict, Optional, List


class Feature2State(TypedDict):
    thread_id: str

    jd_content: Optional[dict]

    candidates: Optional[List[dict]]

    jd_embedding: Optional[List[float]]
    candidate_embeddings: Optional[List[List[float]]]

    ranked_candidates: Optional[List[dict]]
    shortlisted: Optional[List[dict]]

    status: str
    error_message: Optional[str]
