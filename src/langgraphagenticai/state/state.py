from typing import Annotated, List, Any
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict, total=False):
    """
    Represents the structure of the state used in the graph.
    This TypedDict allows additional keys along with the 'messages' key.
    """
    messages: Annotated[List, add_messages]
    requirements: Any
    user_stories: Any
    product_owner_feedback: Any
    design_documents: Any
    design_review_feedback: Any
    code: Any
    code_review_feedback: Any
    security_review_feedback: Any
    test_cases: Any
    test_cases_review_feedback: Any
    qa_testing_results: Any
    deployment_status: Any
    monitoring_feedback: Any
    maintenance_plan: Any
    history:Any
    # Keys for human-in-the-loop feedback
    human_product_owner_feedback: Any
    human_design_review_feedback: Any
    human_code_review_feedback: Any
    human_test_cases_review_feedback: Any
