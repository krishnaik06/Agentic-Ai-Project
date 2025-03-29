import streamlit as st
from langchain_core.messages import AIMessage
import re
import json

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message, user_controls=None):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message
        self.user_controls = user_controls or {}

    def display_result_on_ui(self):
        graph = self.graph
        
        # Initialize state with necessary keys
        initial_state = {
            "messages": [],
            "requirements": "",
            "user_stories": "",
            "approval_feedback": "",
            "design_documents": "",
            "code": "",
            "code_review_feedback": "",
            "security_review_feedback": "",
            "test_cases": "",
            "qa_testing_results": "",
            "deployment_status": "",
            "monitoring_feedback": "",
            "maintenance_plan": "",
            "history": [],  # Ensure history is initialized as an empty list
            # Inject file-uploaded requirements and user approval (if provided)
            "uploaded_requirements": self.user_controls.get("uploaded_requirements", ""),
            "user_approval": self.user_controls.get("user_approval", ""),
            "project_hint": self.user_controls.get("project_hint", "")
        }
        
        try:
            # Run the graph with initial state
            result_state = graph.invoke(initial_state)
            
            # Define the workflow stages
            stages = [
                {"key": "requirements", "title": "Requirements", "icon": "📋", "timestamp_key": "requirements_timestamp"},
                {"key": "user_stories", "title": "User Stories", "icon": "👥", "timestamp_key": "user_stories_timestamp"},
                {"key": "approval_feedback", "title": "Approval Feedback", "icon": "✅", "timestamp_key": "approval_feedback_timestamp"},
                {"key": "design_documents", "title": "Design Documents", "icon": "🏗️", "timestamp_key": "design_documents_timestamp"},
                {"key": "code", "title": "Generated Code", "icon": "💻", "timestamp_key": "code_timestamp"},
                {"key": "code_review_feedback", "title": "Code Review", "icon": "🔍", "timestamp_key": "code_review_timestamp"},
                {"key": "security_review_feedback", "title": "Security Review", "icon": "🔒", "timestamp_key": "security_review_timestamp"},
                {"key": "test_cases", "title": "Test Cases", "icon": "🧪", "timestamp_key": "test_cases_timestamp"},
                {"key": "qa_testing_results", "title": "QA Testing Results", "icon": "📊", "timestamp_key": "qa_testing_timestamp"},
                {"key": "deployment_status", "title": "Deployment Status", "icon": "🚀", "timestamp_key": "deployment_timestamp"},
                {"key": "monitoring_feedback", "title": "Monitoring Feedback", "icon": "📡", "timestamp_key": "monitoring_timestamp"},
                {"key": "maintenance_plan", "title": "Maintenance Plan", "icon": "🔧", "timestamp_key": "maintenance_timestamp"}
            ]
            
            # Add history tab to the list
            all_tabs = [f"{stage['icon']} {stage['title']}" for stage in stages] + ["📜 History"]
            
            # Use tabs for a cleaner display
            tabs = st.tabs(all_tabs)
            
            # Display each stage in its tab
            for i, stage in enumerate(stages):
                with tabs[i]:
                    value = result_state.get(stage["key"], "No output available.")
                    timestamp = result_state.get(stage["timestamp_key"], "")
                    
                    # Display header for the stage
                    st.subheader(f"{stage['icon']} {stage['title']}")
                    
                    # Display timestamp if available
                    if timestamp:
                        st.caption(f"Generated at: {timestamp}")
                    
                    # Add separator
                    st.divider()
                    
                    # Display content
                    if value:
                        if hasattr(value, "content"):
                            content = value.content
                            
                            # Special handling for code section
                            if stage["key"] == "code":
                                self._display_code_as_repo(content)
                            # For test cases, use code blocks
                            elif stage["key"] in ["test_cases"]:
                                # Extract code blocks if present
                                code_blocks = self._extract_code_blocks(content)
                                
                                # Display non-code content first
                                non_code = re.sub(r'```[\s\S]*?```', '', content).strip()
                                if non_code:
                                    st.write(non_code)
                                
                                # Then display code blocks
                                if code_blocks:
                                    for block in code_blocks:
                                        st.code(block["code"], language=block["language"])
                                else:
                                    st.write(content)
                            else:
                                st.write(content)
                        elif isinstance(value, list):
                            for item in value:
                                if hasattr(item, "content"):
                                    st.write(item.content)
                                else:
                                    st.write(item)
                        else:
                            st.write(str(value))
                    else:
                        st.info("No output available for this stage.")
                        
                    # Add download button for relevant stages
                    if stage["key"] in ["requirements", "user_stories", "design_documents", "code", "test_cases", "maintenance_plan"]:
                        if value and hasattr(value, "content"):
                            st.download_button(
                                label=f"Download {stage['title']}",
                                data=value.content,
                                file_name=f"{stage['key']}.txt",
                                mime="text/plain"
                            )
            
            # Display history in the last tab
            with tabs[-1]:
                st.subheader("📜 Workflow History")
                st.divider()
                
                history = result_state.get("history", [])
                
                # Safety check to ensure history is a list
                if not isinstance(history, list):
                    history = []
                    st.warning("History data is not in the expected format. Displaying empty history.")
                
                if history:
                    # Create expandable sections for each history entry
                    for entry in history:
                        # Safety check to ensure entry is a dictionary
                        if not isinstance(entry, dict):
                            continue
                            
                        with st.expander(f"{entry.get('stage', 'Unknown stage')} - {entry.get('timestamp', 'Unknown time')}"):
                            st.write(entry.get('content', 'No content available'))
                else:
                    st.info("No history records available.")
                
                # Add download button for history
                if history:
                    try:
                        history_json = json.dumps(history, indent=2)
                        st.download_button(
                            label="Download Complete History",
                            data=history_json,
                            file_name="sdlc_workflow_history.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"Could not create history download: {e}")
            
        except Exception as e:
            st.error(f"Error processing workflow: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            
    def _extract_code_blocks(self, content):
        """
        Extract code blocks from markdown content.
        Returns a list of dictionaries with code and language.
        """
        import re
        
        # Check if content is a string
        if not isinstance(content, str):
            if hasattr(content, 'content'):
                content = content.content
            else:
                return []
                
        code_blocks = []
        # Match markdown code blocks with language specifier
        pattern = r'```(\w*)\n([\s\S]*?)```'
        matches = re.findall(pattern, content)
        
        for match in matches:
            language, code = match
            code_blocks.append({
                "language": language if language else "text",
                "code": code.strip()
            })
            
        return code_blocks
        
    def _display_code_as_repo(self, content):
        """
        Display code content in a GitHub-like repository format
        """
        # Check if content is a string
        if not isinstance(content, str):
            if hasattr(content, 'content'):
                content = content.content
            else:
                st.error("Invalid content format for code display")
                return
                
        # Extract the code blocks and organize them by file
        code_blocks = self._extract_code_blocks(content)
        
        # Try to identify project structure/files from the content
        project_files = {}
        current_file = None
        
        # Extract file paths using regex patterns
        file_paths = re.findall(r'`([^`]*\.[a-zA-Z0-9]+)`', content)
        file_paths += re.findall(r'\*\*([^*]*\.[a-zA-Z0-9]+)\*\*', content)
        file_paths = list(set(file_paths))  # Remove duplicates
        
        # Match code blocks with file paths if possible
        for block in code_blocks:
            # Try to find a comment or indication of what file this belongs to
            file_hints = re.findall(r'(?:\/\/|#|\/\*)\s*(?:file|filename):\s*([^\n\r]*)', block["code"], re.IGNORECASE)
            if file_hints:
                file_path = file_hints[0].strip()
                project_files[file_path] = {
                    "language": block["language"],
                    "code": block["code"]
                }
        
        # If we couldn't associate all blocks, try to use the file_paths we found
        if len(project_files) < len(code_blocks) and file_paths:
            unmatched_blocks = [b for b in code_blocks if not any(p in project_files and b["code"] in project_files[p]["code"] for p in project_files)]
            for i, block in enumerate(unmatched_blocks):
                if i < len(file_paths):
                    project_files[file_paths[i]] = {
                        "language": block["language"],
                        "code": block["code"]
                    }
        
        # Create file structure visualization
        st.subheader("📁 Project Structure")
        
        # Extract README if it exists
        readme_content = ""
        for path, file_info in project_files.items():
            if "readme" in path.lower():
                readme_content = file_info["code"]
                break
        
        # If no project files identified yet, parse the content to look for file structure
        if not project_files:
            # Look for project structure description
            structure_match = re.search(r'(?:project structure|file structure|directory structure):(.*?)(?:\n\n|\Z)', 
                                       content, re.IGNORECASE | re.DOTALL)
            if structure_match:
                structure_text = structure_match.group(1)
                st.write(structure_text)
            else:
                # Just show all code blocks with their language
                for i, block in enumerate(code_blocks):
                    project_files[f"file_{i+1}.{block['language']}"] = {
                        "language": block["language"],
                        "code": block["code"]
                    }
        
        # Display file structure
        if project_files:
            file_tree = "```\n"
            file_tree += "project-root/\n"
            for path in sorted(project_files.keys()):
                file_tree += f"├── {path}\n"
            file_tree += "```"
            st.code(file_tree, language="")
        else:
            st.info("No files detected in the code output.")
        
        # Show README.md first if it exists
        if readme_content:
            with st.expander("📄 README.md", expanded=True):
                st.markdown(readme_content)
        
        # Show rest of the files
        st.subheader("📄 Source Files")
        for path, file_info in sorted(project_files.items()):
            if "readme" not in path.lower():  # Skip README as it's already shown
                with st.expander(f"📄 {path}"):
                    st.code(file_info["code"], language=file_info["language"])
        
        # Show setup and deployment information
        setup_info = re.search(r'(?:setup instructions|how to run|installation|getting started):(.*?)(?:\n\n|\Z)', 
                              content, re.IGNORECASE | re.DOTALL)
        
        if setup_info:
            st.subheader("🚀 Setup & Deployment")
            st.write(setup_info.group(1))
        
        # Show any non-code content that might be valuable
        non_code = re.sub(r'```[\s\S]*?```', '', content).strip()
        if non_code and len(non_code) > 100:  # Only if it's substantial
            with st.expander("📝 Additional Implementation Notes"):
                st.write(non_code)