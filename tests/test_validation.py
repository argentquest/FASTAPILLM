import pytest
from pydantic import ValidationError as PydanticValidationError
from validation import (
    sanitize_input,
    validate_character_name,
    validate_story_request
)
from exceptions import ValidationError

class TestSanitizeInput:
    def test_sanitize_basic_input(self):
        assert sanitize_input("Hello World") == "Hello World"
    
    def test_sanitize_html_input(self):
        assert sanitize_input("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    
    def test_sanitize_null_bytes(self):
        assert sanitize_input("Hello\x00World") == "HelloWorld"
    
    def test_sanitize_control_characters(self):
        assert sanitize_input("Hello\x01\x02World") == "HelloWorld"
    
    def test_sanitize_whitespace(self):
        assert sanitize_input("  Hello World  ") == "Hello World"
    
    def test_empty_input_raises_error(self):
        with pytest.raises(ValidationError):
            sanitize_input("")

class TestValidateCharacterName:
    def test_valid_character_names(self):
        assert validate_character_name("Santa Claus") == "Santa Claus"
        assert validate_character_name("Rudolph") == "Rudolph"
        assert validate_character_name("Mrs. Claus") == "Mrs. Claus"
        assert validate_character_name("Elf #1") == "Elf #1"
    
    def test_invalid_characters(self):
        with pytest.raises(ValidationError):
            validate_character_name("Santa@Claus")
        
        with pytest.raises(ValidationError):
            validate_character_name("Santa[Claus]")
    
    def test_too_short_name(self):
        with pytest.raises(ValidationError):
            validate_character_name("")
    
    def test_only_whitespace(self):
        with pytest.raises(ValidationError):
            validate_character_name("   ")
    
    def test_only_punctuation(self):
        with pytest.raises(ValidationError):
            validate_character_name("...")

class TestValidateStoryRequest:
    def test_valid_request(self):
        primary, secondary = validate_story_request("Santa", "Rudolph")
        assert primary == "Santa"
        assert secondary == "Rudolph"
    
    def test_same_characters(self):
        with pytest.raises(ValidationError):
            validate_story_request("Santa", "Santa")
    
    def test_same_characters_different_case(self):
        with pytest.raises(ValidationError):
            validate_story_request("Santa", "santa")

