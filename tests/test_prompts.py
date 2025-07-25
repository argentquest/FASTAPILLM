import pytest
from pathlib import Path
from prompts.prompt_utils import load_prompt_file, format_template, validate_template_variables
from prompts.semantic_kernel_prompts import get_chat_messages
from prompts.langchain_prompts import get_langchain_messages
from prompts.langgraph_prompts import get_initial_messages, get_enhancement_messages

class TestPromptUtils:
    def test_load_prompt_file_exists(self):
        """Test loading an existing prompt file"""
        content = load_prompt_file("semantic_kernel/semantic_kernel_system_prompt.txt")
        assert isinstance(content, str)
        assert len(content) > 0
    
    def test_load_prompt_file_not_exists(self):
        """Test loading a non-existent prompt file"""
        with pytest.raises(FileNotFoundError):
            load_prompt_file("nonexistent_prompt.txt")
    
    def test_format_template(self):
        """Test template formatting"""
        template = "Hello {name}, welcome to {place}!"
        result = format_template(template, name="Alice", place="Wonderland")
        assert result == "Hello Alice, welcome to Wonderland!"
    
    def test_format_template_missing_variable(self):
        """Test template formatting with missing variable"""
        template = "Hello {name}, welcome to {place}!"
        with pytest.raises(KeyError):
            format_template(template, name="Alice")  # Missing 'place'
    
    def test_validate_template_variables(self):
        """Test template variable validation"""
        template = "Story with {primary_character} and {secondary_character}"
        assert validate_template_variables(template, ["primary_character", "secondary_character"])
        assert not validate_template_variables(template, ["primary_character", "missing_var"])

class TestSemanticKernelPrompts:
    def test_get_chat_messages(self):
        """Test Semantic Kernel message generation"""
        messages = get_chat_messages("Santa", "Rudolph")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "Santa" in messages[1]["content"]
        assert "Rudolph" in messages[1]["content"]

class TestLangChainPrompts:
    def test_get_langchain_messages(self):
        """Test LangChain message generation"""
        messages = get_langchain_messages("Santa", "Rudolph")
        assert len(messages) == 2
        assert hasattr(messages[0], 'content')  # SystemMessage
        assert hasattr(messages[1], 'content')  # HumanMessage
        assert "Santa" in messages[1].content
        assert "Rudolph" in messages[1].content

class TestLangGraphPrompts:
    def test_get_initial_messages(self):
        """Test LangGraph initial message generation"""
        messages = get_initial_messages("Santa", "Rudolph")
        assert len(messages) == 2
        assert hasattr(messages[0], 'content')  # SystemMessage
        assert hasattr(messages[1], 'content')  # HumanMessage
        assert "Santa" in messages[1].content
        assert "Rudolph" in messages[1].content
    
    def test_get_enhancement_messages(self):
        """Test LangGraph enhancement message generation"""
        test_story = "Once upon a time, Santa met Rudolph."
        messages = get_enhancement_messages(test_story)
        assert len(messages) == 2
        assert hasattr(messages[0], 'content')  # SystemMessage
        assert hasattr(messages[1], 'content')  # HumanMessage
        assert test_story in messages[1].content

class TestPromptFileExistence:
    """Test that all required prompt files exist"""
    
    prompt_files = [
        "semantic_kernel/semantic_kernel_system_prompt.txt",
        "semantic_kernel/semantic_kernel_user_message_template.txt",
        "langchain/langchain_system_prompt.txt",
        "langchain/langchain_user_prompt_template.txt",
        "langgraph/langgraph_storyteller_system_prompt.txt",
        "langgraph/langgraph_initial_story_template.txt",
        "langgraph/langgraph_editor_system_prompt.txt",
        "langgraph/langgraph_enhancement_template.txt"
    ]
    
    @pytest.mark.parametrize("filename", prompt_files)
    def test_prompt_file_exists(self, filename):
        """Test that each required prompt file exists and is not empty"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        file_path = prompts_dir / filename
        assert file_path.exists(), f"Prompt file {filename} does not exist"
        
        content = file_path.read_text(encoding='utf-8').strip()
        assert len(content) > 0, f"Prompt file {filename} is empty"