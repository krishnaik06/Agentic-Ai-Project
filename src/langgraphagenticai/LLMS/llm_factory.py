from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.LLMS.openaillm import OpenAILLM

class LLMFactory:
    @staticmethod
    def create_llm(user_controls):
        selected_llm = user_controls.get("selected_llm")
        
        if selected_llm == "Groq":
            return GroqLLM(user_controls).get_llm_model()
        elif selected_llm == "OpenAI":
            return OpenAILLM(user_controls).get_llm_model()
        else:
            raise ValueError(f"Unsupported LLM provider: {selected_llm}")