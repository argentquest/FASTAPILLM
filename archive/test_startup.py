#!/usr/bin/env python3
"""
Simple test script to verify the application can start without errors.
"""

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        # Test config loading
        from config import settings
        print(f"✓ Config loaded: {settings.app_name}")
        
        # Test models
        from models.story_models import StoryRequest, StoryResponse
        print("✓ Models imported successfully")
        
        # Test validation
        from validation import validate_character_name
        print("✓ Validation imported successfully")
        
        # Test services
        from services.semantic_kernel_service import SemanticKernelService
        from services.langchain_service import LangChainService
        from services.langgraph_service import LangGraphService
        print("✓ Services imported successfully")
        
        # Test prompt loading
        from prompts.semantic_kernel_prompts import get_chat_messages
        messages = get_chat_messages("Test", "Character")
        print(f"✓ Prompts loaded successfully ({len(messages)} messages)")
        
        # Test model validation
        request = StoryRequest(primary_character="Santa", secondary_character="Rudolph")
        print(f"✓ Model validation successful: {request.primary_character} & {request.secondary_character}")
        
        print("\n🎉 All tests passed! Application should start successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)