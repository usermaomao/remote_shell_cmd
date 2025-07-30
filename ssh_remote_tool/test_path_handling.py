#!/usr/bin/env python3
"""
Test script for path handling improvements
"""
import sys
import os
import posixpath

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def normalize_remote_path(path):
    """Normalize remote path to use forward slashes and handle edge cases"""
    if not path:
        return "/"
    
    # Convert to forward slashes
    path = path.replace('\\', '/')
    
    # Ensure it starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    # Remove double slashes
    while '//' in path:
        path = path.replace('//', '/')
    
    # Remove trailing slash unless it's root
    if len(path) > 1 and path.endswith('/'):
        path = path.rstrip('/')
    
    return path

def join_remote_path(base_path, *parts):
    """Join remote path parts using posixpath for consistent forward slashes"""
    # Use posixpath.join for Unix-style paths
    result = posixpath.join(base_path, *parts)
    # Normalize and resolve any ".." components
    result = posixpath.normpath(result)
    return normalize_remote_path(result)

def get_parent_path(path):
    """Get parent directory of given path"""
    path = normalize_remote_path(path)
    if path == "/":
        return "/"
    return posixpath.dirname(path)

def test_path_functions():
    """Test the path handling functions"""
    print("Testing path handling functions...")
    
    # Test normalize_remote_path
    test_cases = [
        ("", "/"),
        ("/", "/"),
        ("home", "/home"),
        ("/home/", "/home"),
        ("/home//user", "/home/user"),
        ("\\home\\user", "/home/user"),
        ("home\\user\\documents", "/home/user/documents"),
        ("//home//user//", "/home/user"),
    ]
    
    print("\nTesting normalize_remote_path:")
    for input_path, expected in test_cases:
        result = normalize_remote_path(input_path)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_path}' -> '{result}' (expected: '{expected}')")
    
    # Test join_remote_path
    print("\nTesting join_remote_path:")
    join_test_cases = [
        (("/", "home"), "/home"),
        (("/home", "user"), "/home/user"),
        (("/home/user", "documents"), "/home/user/documents"),
        (("/home/user", ".."), "/home"),
        (("/", "home", "user", "documents"), "/home/user/documents"),
    ]
    
    for (base_and_parts, expected) in join_test_cases:
        base = base_and_parts[0]
        parts = base_and_parts[1:]
        result = join_remote_path(base, *parts)
        status = "✓" if result == expected else "✗"
        print(f"  {status} join('{base}', {parts}) -> '{result}' (expected: '{expected}')")
    
    # Test get_parent_path
    print("\nTesting get_parent_path:")
    parent_test_cases = [
        ("/", "/"),
        ("/home", "/"),
        ("/home/user", "/home"),
        ("/home/user/documents", "/home/user"),
    ]
    
    for input_path, expected in parent_test_cases:
        result = get_parent_path(input_path)
        status = "✓" if result == expected else "✗"
        print(f"  {status} parent('{input_path}') -> '{result}' (expected: '{expected}')")

if __name__ == "__main__":
    test_path_functions()
    print("\nPath handling test completed!")
