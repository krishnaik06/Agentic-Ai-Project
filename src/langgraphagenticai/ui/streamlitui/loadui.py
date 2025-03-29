import streamlit as st
from datetime import date
from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()  # config
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title="🤖 SDLC Workflow Agent", layout="wide")
        st.header("🤖 Software Development Lifecycle (SDLC) Workflow Agent")
        
        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()
            
            # Add project hint input
            st.markdown("### Project Information")
            self.user_controls["project_hint"] = st.text_area(
                "Project Description",
                placeholder="Describe your project in a few sentences (e.g., 'A task management app with user authentication and team collaboration features')",
                help="Providing a brief description will help generate more relevant requirements and code."
            )
            
            st.markdown("---")
            
            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)
            self.user_controls["selected_usecase"] = "Software Lifecycle"  # Fixed to Software Lifecycle

            # Handle different LLM options
            if self.user_controls["selected_llm"] == 'Groq':
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                # API key input
                self.user_controls["GROQ_API_KEY"] = st.session_state.get("GROQ_API_KEY", "")
                api_key_input = st.text_input("Groq API Key", 
                                             type="password", 
                                             value=self.user_controls["GROQ_API_KEY"],
                                             help="Your API key will be stored in the session for convenience")
                
                # Only update if changed to avoid overwriting in session
                if api_key_input != self.user_controls["GROQ_API_KEY"]:
                    self.user_controls["GROQ_API_KEY"] = api_key_input
                    st.session_state["GROQ_API_KEY"] = api_key_input
                
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Get a key at: https://console.groq.com/keys")
            
            elif self.user_controls["selected_llm"] == 'OpenAI':
                # Model selection for OpenAI
                model_options = self.config.get_openai_model_options()
                self.user_controls["selected_openai_model"] = st.selectbox("Select Model", model_options)
                # API key input for OpenAI
                self.user_controls["OPENAI_API_KEY"] = st.session_state.get("OPENAI_API_KEY", "")
                api_key_input = st.text_input("OpenAI API Key", 
                                             type="password", 
                                             value=self.user_controls["OPENAI_API_KEY"],
                                             help="Your API key will be stored in the session for convenience")
                
                # Only update if changed to avoid overwriting in session
                if api_key_input != self.user_controls["OPENAI_API_KEY"]:
                    self.user_controls["OPENAI_API_KEY"] = api_key_input
                    st.session_state["OPENAI_API_KEY"] = api_key_input
                
                if not self.user_controls["OPENAI_API_KEY"]:
                    st.warning("⚠️ Please enter your OpenAI API key to proceed. Get a key at: https://platform.openai.com/api-keys")
            
            # elif self.user_controls["selected_llm"] == 'Anthropic':
            #     # Placeholder for Anthropic - you would need to implement this similar to the others
            #     st.info("Anthropic integration will be implemented in a future update")
                
            st.markdown("---")
            
            # Requirements File Upload
            st.markdown("### Upload Requirements File")
            uploaded_file = st.file_uploader(
                "Choose a requirements file", 
                type=["txt", "docx", "pdf"],
                help="Upload a file containing your project requirements. Supported formats: TXT, DOCX, PDF"
            )
            
            if uploaded_file:
                try:
                    # Read file content (assuming text content for simplicity)
                    file_content = uploaded_file.read().decode("utf-8")
                    self.user_controls["uploaded_requirements"] = file_content
                    st.success(f"Requirements file '{uploaded_file.name}' uploaded successfully!")
                    
                    # Show a preview
                    with st.expander("Preview uploaded requirements"):
                        st.text(file_content[:500] + ("..." if len(file_content) > 500 else ""))
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    self.user_controls["uploaded_requirements"] = ""
            else:
                self.user_controls["uploaded_requirements"] = ""
                st.info("No requirements file uploaded. The system will generate sample requirements based on the project description if provided.")
            
            st.markdown("---")
            
            # User approval section
            st.markdown("### User Approval")
            st.info("After reviewing the user stories, you can provide your approval or feedback below.")
            self.user_controls["user_approval"] = st.text_area(
                "Approval Feedback (Optional)", 
                help="Enter your feedback on the generated user stories. Leave empty for auto-approval."
            )
            
            # Advanced options
            with st.expander("Advanced Options"):
                st.markdown("### SDLC Workflow Configuration")
                self.user_controls["skip_security_review"] = st.toggle(
                    "Skip Security Review", 
                    value=False,
                    help="Enable to skip the security review step in the SDLC workflow"
                )
                
                self.user_controls["generate_detailed_tests"] = st.toggle(
                    "Generate Detailed Tests", 
                    value=True,
                    help="Enable to generate more comprehensive test cases"
                )
            
            st.markdown("---")
            
            # Run workflow button
            self.user_controls["run_workflow"] = st.button(
                "Run SDLC Workflow", 
                type="primary",
                use_container_width=True
            )
            
            # Additional information
            if not self.user_controls["run_workflow"]:
                st.info("Click the button above to start the SDLC workflow process. This may take several minutes to complete.")

        return self.user_controls