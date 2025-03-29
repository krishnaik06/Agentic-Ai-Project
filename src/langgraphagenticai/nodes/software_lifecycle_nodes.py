from src.langgraphagenticai.state.state import State
from langchain_core.messages import AIMessage
import datetime

class RequirementsNode:
    """
    Node to capture user-provided software requirements.
    Uses an uploaded requirements file if available; otherwise, prompts the LLM.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        # Get requirements from uploaded file
        uploaded = state.get("uploaded_requirements", "")
        if uploaded:
            # Use LLM to process and structure the requirements from the uploaded file
            prompt = f"You are a requirements analyst. Based on these requirements, please organize and structure them into a formal requirements document with clear sections for functional and non-functional requirements, constraints, and assumptions:\n\n{uploaded}"
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            requirements = AIMessage(content=f"Requirements processed from uploaded file:\n\n{response.content}")
        else:
            # Generate sample requirements if none are provided
            project_hint = state.get("project_hint", "")
            if project_hint:
                prompt = f"Please generate comprehensive software requirements for the following project: {project_hint}"
            else:
                prompt = "Please generate comprehensive software requirements for a typical enterprise web application project."
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            requirements = AIMessage(content=f"Auto-generated requirements:\n\n{response.content}")
        
        # Record timestamp for history tracking
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["requirements"] = requirements
        state["requirements_timestamp"] = timestamp
        
        # Initialize history if not present
        if "history" not in state:
            state["history"] = []
            
        # Add to history
        state["history"].append({
            "stage": "Requirements",
            "timestamp": timestamp,
            "content": requirements.content
        })
        
        return state

class UserStoriesNode:
    """
    Node to auto-generate user stories based on requirements.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        req = state.get("requirements", "")
        prompt = f"""
        As a product manager, create detailed user stories based on these requirements. 
        Format each user story with:
        - A clear title
        - "As a [role], I want to [action], so that [benefit]" format
        - Acceptance criteria
        - Priority level (High/Medium/Low)
        - Estimated effort (S/M/L/XL)
        
        Requirements:
        {req.content if hasattr(req, 'content') else req}
        """
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["user_stories"] = AIMessage(content=response.content)
        state["user_stories_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "User Stories",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class ApprovalNode:
    """
    Node for handling user approval of the generated user stories.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        stories = state.get("user_stories", "")
        user_approval = state.get("user_approval", "")
        
        if user_approval:
            # Use the provided approval feedback
            content = f"User approval feedback:\n\n{user_approval}"
            approval_feedback = AIMessage(content=content)
        else:
            # Auto-approve with generated feedback for automation
            prompt = f"Review these user stories as a product owner and provide constructive feedback along with your approval decision (Approved/Needs Revision). For each user story that needs revision, clearly state what should be changed:\n\n{stories.content if hasattr(stories, 'content') else stories}"
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            approval_feedback = AIMessage(content=f"Auto-generated approval feedback:\n\n{response.content}")
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["approval_feedback"] = approval_feedback
        state["approval_feedback_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Approval Feedback",
            "timestamp": timestamp,
            "content": approval_feedback.content
        })
        
        return state

class DesignDocumentsNode:
    """
    Node to create design documents (functional and technical) based on user stories.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        stories = state.get("user_stories", "")
        approval = state.get("approval_feedback", "")
        
        prompt = f"""
        Based on these user stories and approval feedback, create comprehensive design documents including:
        
        1. System Architecture:
           - High-level architecture diagram (described in text)
           - Components and their interactions
           - Data flow
           
        2. Technical Design:
           - Backend technology stack
           - Frontend technology stack
           - Database schema design
           - API endpoints specification
           
        3. UX/UI Design:
           - User flow descriptions
           - Key screens/pages description
           
        User Stories:
        {stories.content if hasattr(stories, 'content') else stories}
        
        Approval Feedback:
        {approval.content if hasattr(approval, 'content') else approval}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["design_documents"] = AIMessage(content=response.content)
        state["design_documents_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Design Documents",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class CodeGenerationNode:
    """
    Node to generate initial code from the design documents.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        design_docs = state.get("design_documents", "")
        prompt = f"""
        Based on these design documents, generate the core code for the application. Include:
        
        1. Project structure (folder organization)
        2. Key files with implementation code
        3. Database models
        4. API endpoints
        5. Frontend components (if applicable)
        6. Dockerfile and docker-compose.yml (if applicable)
        7. README.md with setup and running instructions
        
        Make sure to include meaningful comments and follow best practices.
        
        Design Documents:
        {design_docs.content if hasattr(design_docs, 'content') else design_docs}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["code"] = AIMessage(content=response.content)
        state["code_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Code Generation",
            "timestamp": timestamp,
            "content": "Code generated. See the Code section for details."
        })
        
        return state

class CodeReviewNode:
    """
    Node to review the generated code and provide feedback.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        code = state.get("code", "")
        prompt = f"""
        As a senior developer conducting a code review, please review the following code and provide detailed feedback:
        
        1. Code quality assessment
        2. Potential bugs or issues
        3. Performance concerns
        4. Security considerations
        5. Adherence to best practices
        6. Specific improvement suggestions with code examples
        7. Overall assessment (Pass/Needs Improvements)
        
        Code:
        {code.content if hasattr(code, 'content') else code}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["code_review_feedback"] = AIMessage(content=response.content)
        state["code_review_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Code Review",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class SecurityReviewNode:
    """
    Node to perform a security review on the generated code.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        code = state.get("code", "")
        prompt = f"""
        As a security engineer, conduct a comprehensive security review for the following code. Address:
        
        1. OWASP Top 10 vulnerabilities check
        2. Authentication and authorization vulnerabilities
        3. Data validation and sanitization issues
        4. Secure coding practices assessment
        5. Dependency security concerns
        6. Risk level for each identified issue (High/Medium/Low)
        7. Remediation steps with code examples
        8. Security test plan recommendations
        
        Code:
        {code.content if hasattr(code, 'content') else code}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["security_review_feedback"] = AIMessage(content=response.content)
        state["security_review_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Security Review",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class TestCasesNode:
    """
    Node to generate test cases based on the code.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        code = state.get("code", "")
        user_stories = state.get("user_stories", "")
        
        prompt = f"""
        Create a comprehensive test suite for the application, including:
        
        1. Unit tests for key components
        2. Integration tests
        3. API tests
        4. End-to-end tests
        5. Performance tests
        6. Edge cases and error handling tests
        
        For each test, include:
        - Test ID and name
        - Test description
        - Preconditions
        - Test steps
        - Expected results
        - Test data required
        
        Include actual test code implementation where appropriate.
        
        Code:
        {code.content if hasattr(code, 'content') else code}
        
        User Stories:
        {user_stories.content if hasattr(user_stories, 'content') else user_stories}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["test_cases"] = AIMessage(content=response.content)
        state["test_cases_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Test Cases",
            "timestamp": timestamp,
            "content": "Test cases generated. See the Test Cases section for details."
        })
        
        return state

class QATestingNode:
    """
    Node to simulate QA testing using the generated test cases.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        test_cases = state.get("test_cases", "")
        prompt = f"""
        As a QA engineer, simulate the execution of these test cases and report the testing results. Include:
        
        1. Test execution summary (tests passed/failed/blocked)
        2. Test coverage metrics
        3. Detailed results for each test case
        4. Issues and bugs found (with severity and priority)
        5. Screenshots or descriptions of key issues (described in text)
        6. Recommendations for fixing identified issues
        7. Overall quality assessment
        
        Test Cases:
        {test_cases.content if hasattr(test_cases, 'content') else test_cases}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["qa_testing_results"] = AIMessage(content=response.content)
        state["qa_testing_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "QA Testing",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class DeploymentNode:
    """
    Node to deploy the application.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        code = state.get("code", "")
        qa_results = state.get("qa_testing_results", "")
        
        prompt = f"""
        Create a comprehensive deployment plan and document the simulated deployment process. Include:
        
        1. Deployment architecture
        2. Infrastructure requirements (cloud services, servers, etc.)
        3. CI/CD pipeline configuration
        4. Deployment scripts
        5. Environment setup instructions
        6. Rollback procedures
        7. Post-deployment verification steps
        8. Deployment checklist
        9. Status report after simulated deployment
        
        Code:
        {code.content if hasattr(code, 'content') else code}
        
        QA Testing Results:
        {qa_results.content if hasattr(qa_results, 'content') else qa_results}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["deployment_status"] = AIMessage(content=response.content)
        state["deployment_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Deployment",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class MonitoringFeedbackNode:
    """
    Node to monitor the deployed application and gather feedback.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        deployment = state.get("deployment_status", "")
        
        prompt = f"""
        Simulate the monitoring of the application post-deployment for 2 weeks and provide comprehensive operational feedback. Include:
        
        1. Key performance metrics
        2. Resource utilization
        3. Error rates and common issues
        4. User feedback and satisfaction metrics
        5. System stability assessment
        6. Security incidents (if any)
        7. Scaling considerations based on usage patterns
        8. Recommendations for immediate improvements
        
        Deployment Status:
        {deployment.content if hasattr(deployment, 'content') else deployment}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["monitoring_feedback"] = AIMessage(content=response.content)
        state["monitoring_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Monitoring Feedback",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state

class MaintenanceUpdatesNode:
    """
    Node to generate a maintenance and update plan based on monitoring feedback.
    """
    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> dict:
        feedback = state.get("monitoring_feedback", "")
        prompt = f"""
        Based on the monitoring feedback, create a comprehensive maintenance and update plan. Include:
        
        1. Prioritized list of issues to address
        2. Feature enhancements for next release
        3. Performance optimization plan
        4. Security updates and patches
        5. Database maintenance procedures
        6. Backup and disaster recovery review
        7. Documentation updates needed
        8. Training requirements for support team
        9. Timeline and resource allocation for maintenance activities
        
        Monitoring Feedback:
        {feedback.content if hasattr(feedback, 'content') else feedback}
        """
        
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        
        # Record timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["maintenance_plan"] = AIMessage(content=response.content)
        state["maintenance_timestamp"] = timestamp
        
        # Add to history
        state["history"].append({
            "stage": "Maintenance Plan",
            "timestamp": timestamp,
            "content": response.content
        })
        
        return state