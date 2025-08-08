#!/usr/bin/env python3
"""
Script to fix imports in backend modules for both direct execution and package import
"""

import os
import re

# Map of modules that were moved to backend
MOVED_MODULES = {
    'app_config', 'config', 'custom_settings', 'database', 'exceptions',
    'logging_config', 'middleware', 'pricing', 'rate_limiting', 'retry_utils',
    'transaction_context', 'validation', 'simple_rate_limiting'
}

def fix_import_in_file(filepath):
    """Fix imports in a single file"""
    print(f"Fixing imports in {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports for moved modules
    for module in MOVED_MODULES:
        # Pattern: from module import ...
        pattern1 = rf'^from {module} import (.+)$'
        replacement1 = rf'''try:
    from {module} import \1
except ImportError:
    from .{module} import \1'''
        
        if re.search(pattern1, content, re.MULTILINE):
            content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
        
        # Pattern: import module
        pattern2 = rf'^import {module}$'
        replacement2 = rf'''try:
    import {module}
except ImportError:
    from . import {module}'''
        
        if re.search(pattern2, content, re.MULTILINE):
            content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
    else:
        print(f"  - No changes needed for {filepath}")

def main():
    backend_dir = 'backend'
    
    # Fix Python files in backend directory
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                filepath = os.path.join(root, file)
                fix_import_in_file(filepath)

if __name__ == '__main__':
    main()