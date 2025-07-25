import re
from typing import Optional
import html
import unicodedata

from config import settings
from exceptions import ValidationError
from logging_config import get_logger

logger = get_logger(__name__)

def detect_suspicious_patterns(text: str) -> list[str]:
    """Detect potentially malicious patterns in input text.
    
    Scans the input text for common injection attack patterns including
    SQL injection, XSS (cross-site scripting), and command injection.
    
    Args:
        text: The input text to scan for suspicious patterns.
        
    Returns:
        A list of detected pattern types. Possible values include:
        - 'sql_injection': SQL injection patterns detected
        - 'xss_attempt': Cross-site scripting patterns detected
        - 'command_injection': Command injection patterns detected
        
    Examples:
        >>> detect_suspicious_patterns("SELECT * FROM users")
        []
        >>> detect_suspicious_patterns("'; DROP TABLE users; --")
        ['sql_injection']
        >>> detect_suspicious_patterns("<script>alert('XSS')</script>")
        ['xss_attempt']
    """
    suspicious_patterns = []
    
    # SQL injection patterns
    sql_patterns = [
        r"(\bor\b|\band\b)[\s\d]*['\"]*[\s\d]*=[\s\d]*['\"]*[\s\d]*",
        r"union[\s\d]*select",
        r"drop[\s\d]*table",
        r"delete[\s\d]*from",
        r"insert[\s\d]*into",
        r"update[\s\d]*set"
    ]
    
    # XSS patterns
    xss_patterns = [
        r"<script[\s\S]*?>[\s\S]*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[\s\S]*?>",
        r"<object[\s\S]*?>",
        r"<embed[\s\S]*?>"
    ]
    
    # Command injection patterns
    command_patterns = [
        r"[;&|`$]",
        r"\.\./",
        r"/etc/passwd",
        r"/bin/",
        r"cmd\.exe",
        r"powershell"
    ]
    
    text_lower = text.lower()
    
    for pattern in sql_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            suspicious_patterns.append("sql_injection")
            break
    
    for pattern in xss_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            suspicious_patterns.append("xss_attempt")
            break
            
    for pattern in command_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            suspicious_patterns.append("command_injection")
            break
    
    return suspicious_patterns

def sanitize_input(text: str, field_name: str = "input") -> str:
    """Sanitize user input to prevent injection attacks.
    
    Performs comprehensive sanitization of user input including:
    - Detection of suspicious patterns
    - Removal of null bytes
    - Unicode normalization
    - HTML escaping
    - Control character removal
    - Whitespace trimming
    
    Args:
        text: The input text to sanitize.
        field_name: The name of the field being sanitized (for logging).
            Defaults to "input".
            
    Returns:
        The sanitized text with all potentially harmful content removed
        or escaped.
        
    Raises:
        ValidationError: If the input text is empty or None.
        
    Examples:
        >>> sanitize_input("Hello World")
        'Hello World'
        >>> sanitize_input("<script>alert('XSS')</script>")
        '&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;'
        >>> sanitize_input("  trim me  ")
        'trim me'
    """
    logger.debug("Starting input sanitization", 
                field_name=field_name, 
                input_length=len(text) if text else 0)
    
    if not text:
        logger.warning("Empty input validation failed", field_name=field_name)
        raise ValidationError(f"{field_name} cannot be empty")
    
    original_text = text
    original_length = len(text)
    
    # Check for suspicious patterns before sanitization
    suspicious_patterns = detect_suspicious_patterns(text)
    if suspicious_patterns:
        logger.warning("Suspicious input patterns detected", 
                      field_name=field_name,
                      patterns=suspicious_patterns,
                      input_preview=text[:50] + "..." if len(text) > 50 else text)
    
    # Remove any null bytes
    if '\x00' in text:
        logger.warning("Null bytes detected in input", field_name=field_name)
        text = text.replace('\x00', '')
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # HTML escape
    text = html.escape(text)
    
    # Remove control characters except newlines and tabs
    control_chars_removed = len(re.findall(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', text))
    if control_chars_removed > 0:
        logger.warning("Control characters removed from input", 
                      field_name=field_name, 
                      count=control_chars_removed)
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    sanitization_changes = (original_text != text)
    if sanitization_changes:
        logger.info("Input sanitized", 
                   field_name=field_name,
                   original_length=original_length,
                   sanitized_length=len(text),
                   changes_made=True,
                   suspicious_patterns=suspicious_patterns if suspicious_patterns else None)
    else:
        logger.debug("Input sanitization completed, no changes needed", 
                    field_name=field_name)
    
    return text

def validate_character_name(name: str, field_name: str = "character") -> str:
    """Validate and sanitize character names.
    
    Ensures character names meet all requirements including:
    - Proper sanitization
    - Length constraints
    - Valid character set (letters, numbers, spaces, basic punctuation)
    - Contains at least one alphanumeric character
    
    Args:
        name: The character name to validate.
        field_name: The name of the field being validated (for error messages).
            Defaults to "character".
            
    Returns:
        The validated and sanitized character name.
        
    Raises:
        ValidationError: If the name fails any validation criteria:
            - Empty or None
            - Too short (less than min_character_length)
            - Too long (more than max_character_length)
            - Contains invalid characters
            - Contains no alphanumeric characters
            
    Examples:
        >>> validate_character_name("John Doe")
        'John Doe'
        >>> validate_character_name("R2-D2")
        'R2-D2'
        >>> validate_character_name("!!!")
        ValidationError: character must contain at least one letter or number
    """
    logger.debug("Starting character name validation", 
                field_name=field_name, 
                input_length=len(name) if name else 0)
    
    try:
        # First sanitize
        name = sanitize_input(name, field_name)
        
        # Check length
        if len(name) < settings.min_character_length:
            logger.warning("Character name too short", 
                          field_name=field_name,
                          length=len(name),
                          min_required=settings.min_character_length)
            raise ValidationError(
                f"{field_name} must be at least {settings.min_character_length} character(s) long"
            )
        
        if len(name) > settings.max_character_length:
            logger.warning("Character name too long", 
                          field_name=field_name,
                          length=len(name),
                          max_allowed=settings.max_character_length)
            raise ValidationError(
                f"{field_name} must be no more than {settings.max_character_length} characters long"
            )
        
        # Check for valid characters (letters, numbers, spaces, and common punctuation)
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.,!?]+$', name):
            invalid_chars = re.findall(r'[^a-zA-Z0-9\s\-\'\.,!?]', name)
            logger.warning("Invalid characters in character name", 
                          field_name=field_name,
                          invalid_chars=list(set(invalid_chars)),
                          name_preview=name[:30] + "..." if len(name) > 30 else name)
            raise ValidationError(
                f"{field_name} contains invalid characters. Only letters, numbers, spaces, and basic punctuation are allowed"
            )
        
        # Check that it's not just whitespace or punctuation
        if not re.search(r'[a-zA-Z0-9]', name):
            logger.warning("Character name contains no alphanumeric characters", 
                          field_name=field_name,
                          name_preview=name[:30] + "..." if len(name) > 30 else name)
            raise ValidationError(f"{field_name} must contain at least one letter or number")
        
        logger.debug("Character name validation successful", 
                    field_name=field_name,
                    validated_length=len(name))
        return name
        
    except ValidationError as e:
        logger.error("Character name validation failed", 
                    field_name=field_name,
                    error=str(e),
                    input_preview=name[:30] + "..." if name and len(name) > 30 else name)
        raise

def validate_story_request(primary_character: str, secondary_character: str) -> tuple[str, str]:
    """Validate story generation request.
    
    Validates both primary and secondary character names and ensures
    they are different from each other.
    
    Args:
        primary_character: The name of the primary character.
        secondary_character: The name of the secondary character.
        
    Returns:
        A tuple containing (validated_primary, validated_secondary)
        character names after sanitization and validation.
        
    Raises:
        ValidationError: If either character name fails validation or
            if both character names are the same (case-insensitive).
            
    Examples:
        >>> validate_story_request("Alice", "Bob")
        ('Alice', 'Bob')
        >>> validate_story_request("  Sherlock Holmes  ", "Dr. Watson")
        ('Sherlock Holmes', 'Dr. Watson')
        >>> validate_story_request("John", "john")
        ValidationError: Primary and secondary characters must be different
    """
    logger.info("Starting story request validation",
               primary_length=len(primary_character) if primary_character else 0,
               secondary_length=len(secondary_character) if secondary_character else 0)
    
    try:
        primary = validate_character_name(primary_character, "Primary character")
        secondary = validate_character_name(secondary_character, "Secondary character")
        
        # Check that characters are different
        if primary.lower() == secondary.lower():
            logger.warning("Duplicate character names provided",
                          primary_character=primary,
                          secondary_character=secondary)
            raise ValidationError("Primary and secondary characters must be different")
        
        logger.info("Story request validation successful",
                   primary_character=primary,
                   secondary_character=secondary,
                   total_length=len(primary) + len(secondary))
        
        return primary, secondary
        
    except ValidationError as e:
        logger.error("Story request validation failed",
                    error=str(e),
                    primary_preview=primary_character[:20] + "..." if primary_character and len(primary_character) > 20 else primary_character,
                    secondary_preview=secondary_character[:20] + "..." if secondary_character and len(secondary_character) > 20 else secondary_character)
        raise

