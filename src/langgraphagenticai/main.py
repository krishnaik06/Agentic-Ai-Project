import streamlit as st
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit

def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    Initializes the UI, configures the LLM model, sets up the graph for the SDLC workflow,
    and displays the output in a user-friendly format.
    """
    # Initialize session state if not already done
    if "app_state" not in st.session_state:
        st.session_state.app_state = "initial"
    
    # Initialize UI components
    ui = LoadStreamlitUI()
    user_controls = ui.load_streamlit_ui()

    if not user_controls:
        st.error("Error: Failed to load user input from the UI.")
        return

    # Only execute the workflow when the Run button is clicked
    if user_controls.get("run_workflow"):
        try:
            # Check if API key is provided when using Groq
            if user_controls.get("selected_llm") == 'Groq' and not user_controls.get("GROQ_API_KEY"):
                st.error("Error: Groq API key is required. Please enter your API key in the sidebar.")
                return
            
            with st.spinner("Initializing LLM model..."):
                obj_llm_config = GroqLLM(user_controls_input=user_controls)
                model = obj_llm_config.get_llm_model()
                
                if not model:
                    st.error("Error: LLM model could not be initialized. Please check your API key.")
                    return

            # Always use "Software Lifecycle" usecase
            usecase = "Software Lifecycle"
            
            # Update application state
            st.session_state.app_state = "processing"
            
            # Display progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Setting up the workflow...")
            progress_bar.progress(10)
            
            try:
                graph_builder = GraphBuilder(model)
                graph = graph_builder.setup_graph(usecase)
                
                status_text.text("Workflow setup complete. Running the SDLC process...")
                progress_bar.progress(20)
                
                # Create a container for the results
                results_container = st.container()
                
                with st.spinner("Running the SDLC workflow... This may take a few minutes."):
                    # Update progress for each major step
                    status_updates = [
                        "Generating requirements...",
                        "Creating user stories...",
                        "Processing approval feedback...",
                        "Designing system architecture...",
                        "Generating code...",
                        "Performing code review...",
                        "Running security analysis...",
                        "Creating test cases...",
                        "Executing QA testing...",
                        "Setting up deployment...",
                        "Collecting monitoring data...",
                        "Finalizing maintenance plan..."
                    ]
                    
                    # Simulate progress updates
                    import time
                    for i, update in enumerate(status_updates):
                        progress = 20 + (i + 1) * 5
                        if progress > 95:
                            progress = 95
                        status_text.text(update)
                        progress_bar.progress(progress)
                        time.sleep(0.5)  # Brief delay for visual effect
                    
                    # Display results in the container
                    with results_container:
                        # User message is not needed for SDLC workflow, pass empty string
                        DisplayResultStreamlit(usecase, graph, "", user_controls=user_controls).display_result_on_ui()
                    
                    # Complete the progress bar
                    status_text.text("SDLC workflow completed successfully!")
                    progress_bar.progress(100)
                    
                    # Update application state
                    st.session_state.app_state = "completed"
                    
            except Exception as e:
                st.error(f"Error: Graph setup or execution failed - {e}")
                st.error("Please check your configuration and try again.")
                # Update application state
                st.session_state.app_state = "error"
                return

        except Exception as e:
            st.error(f"Error occurred: {e}")
            # Update application state
            st.session_state.app_state = "error"
    else:
        # Display welcome message when the app first loads
        st.markdown("""
        ## Welcome to the SDLC Workflow Agent
        
        This application automates the entire software development lifecycle process:
        
        1. **Requirements Analysis**: Define what your software needs to do
        2. **User Stories**: Convert requirements into actionable user stories
        3. **Design**: Create system architecture and technical designs
        4. **Implementation**: Generate initial code based on the design
        5. **Testing**: Create test cases and perform QA testing
        6. **Deployment**: Set up deployment plans and procedures
        7. **Maintenance**: Monitor the application and plan updates
        
        ### Getting Started:
        
        1. **Describe your project** in the sidebar (optional but recommended)
        2. **Upload a requirements file** (optional) or let the system generate requirements
        3. **Select your LLM** provider and enter API credentials
        4. **Click "Run SDLC Workflow"** to start the process
        """)
        
        # Display a sample workflow diagram
        st.markdown("""
        ### SDLC Workflow Stages
        ```
        Requirements → User Stories → Approval → Design → Code Generation → 
        Code Review → Security Review → Test Cases → QA Testing → 
        Deployment → Monitoring → Maintenance
        ```
        """)
        
        # Display tips for best results
        st.info("""
        **💡 Tips for best results:**
        
        - Provide a clear project description to get more relevant requirements
        - Upload a detailed requirements file if available
        - Review the generated user stories and provide feedback before proceeding with the full workflow
        - For complex projects, consider using more capable LLM models
        """)
        
        # Show a visual representation of the workflow
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### Planning Phase")
            st.markdown("- Requirements Analysis")
            st.markdown("- User Stories Creation")
            st.markdown("- Design Documents")
        
        with col2:
            st.markdown("#### Development Phase")
            st.markdown("- Code Generation")
            st.markdown("- Code Review")
            st.markdown("- Security Review")
            st.markdown("- Test Case Creation")
        
        with col3:
            st.markdown("#### Operations Phase")
            st.markdown("- QA Testing")
            st.markdown("- Deployment")
            st.markdown("- Monitoring")
            st.markdown("- Maintenance")