from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.nodes.software_lifecycle_nodes import (
    RequirementsNode,
    UserStoriesNode,
    ApprovalNode,
    DesignDocumentsNode,
    CodeGenerationNode,
    CodeReviewNode,
    SecurityReviewNode,
    TestCasesNode,
    QATestingNode,
    DeploymentNode,
    MonitoringFeedbackNode,
    MaintenanceUpdatesNode
)

class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def software_lifecycle_build_graph(self):
        """
        Builds the Software Development Lifecycle graph with appropriate approval checkpoints.
        """
        # Instantiate the lifecycle nodes
        req_node = RequirementsNode(self.llm)
        user_stories_node = UserStoriesNode(self.llm)
        approval_node = ApprovalNode(self.llm)
        design_docs_node = DesignDocumentsNode(self.llm)
        code_gen_node = CodeGenerationNode(self.llm)
        code_review_node = CodeReviewNode(self.llm)
        security_review_node = SecurityReviewNode(self.llm)
        test_cases_node = TestCasesNode(self.llm)
        qa_testing_node = QATestingNode(self.llm)
        deployment_node = DeploymentNode(self.llm)
        monitoring_node = MonitoringFeedbackNode(self.llm)
        maintenance_node = MaintenanceUpdatesNode(self.llm)

        # Add nodes using unique IDs (avoiding conflict with state keys)
        self.graph_builder.add_node("initialize_state", self._initialize_state)
        self.graph_builder.add_node("requirements_node", req_node.process)
        self.graph_builder.add_node("user_stories_node", user_stories_node.process)
        self.graph_builder.add_node("approval_node", approval_node.process)
        self.graph_builder.add_node("design_documents_node", design_docs_node.process)
        self.graph_builder.add_node("code_generation_node", code_gen_node.process)
        self.graph_builder.add_node("code_review_node", code_review_node.process)
        self.graph_builder.add_node("security_review_node", security_review_node.process)
        self.graph_builder.add_node("test_cases_node", test_cases_node.process)
        self.graph_builder.add_node("qa_testing_node", qa_testing_node.process)
        self.graph_builder.add_node("deployment_node", deployment_node.process)
        self.graph_builder.add_node("monitoring_feedback_node", monitoring_node.process)
        self.graph_builder.add_node("maintenance_updates_node", maintenance_node.process)

        # Define the workflow edges using the unique node IDs
        self.graph_builder.add_edge(START, "initialize_state")
        self.graph_builder.add_edge("initialize_state", "requirements_node")
        self.graph_builder.add_edge("requirements_node", "user_stories_node")
        self.graph_builder.add_edge("user_stories_node", "approval_node")
        self.graph_builder.add_edge("approval_node", "design_documents_node")
        self.graph_builder.add_edge("design_documents_node", "code_generation_node")
        self.graph_builder.add_edge("code_generation_node", "code_review_node")
        self.graph_builder.add_edge("code_review_node", "security_review_node")
        self.graph_builder.add_edge("security_review_node", "test_cases_node")
        self.graph_builder.add_edge("test_cases_node", "qa_testing_node")
        self.graph_builder.add_edge("qa_testing_node", "deployment_node")
        self.graph_builder.add_edge("deployment_node", "monitoring_feedback_node")
        self.graph_builder.add_edge("monitoring_feedback_node", "maintenance_updates_node")
        self.graph_builder.add_edge("maintenance_updates_node", END)
    
    def _initialize_state(self, state: State) -> dict:
        """Initialize the state with required keys to prevent 'history' errors."""
        if "history" not in state:
            state["history"] = []
        return state

    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Software Lifecycle":
            self.software_lifecycle_build_graph()
        else:
            raise ValueError(f"Unsupported use case: {usecase}")

        return self.graph_builder.compile()