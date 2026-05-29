#!/usr/bin/env python3
"""
Test script to verify installation
"""

import sys
import importlib


def test_python_version():
    """Check Python version"""
    print("✓ Python version:", sys.version)
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    return True


def test_dependencies():
    """Check if all dependencies are installed"""
    dependencies = [
        'flask',
        'flask_cors',
        'requests',
        'anthropic',
        'dotenv'
    ]

    all_ok = True
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep} installed")
        except ImportError:
            print(f"✗ {dep} not installed")
            all_ok = False

    return all_ok


def test_config():
    """Check configuration"""
    try:
        from config import Config
        print("✓ Config loaded")

        if Config.CLAUDE_API_KEY:
            print("✓ Claude API key configured")
        else:
            print("⚠ Claude API key not configured (set CLAUDE_API_KEY in .env)")

        if Config.GITHUB_TOKEN:
            print("✓ GitHub token configured")
        else:
            print("⚠ GitHub token not configured (optional for public repos)")

        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False


def test_services():
    """Check if services can be imported"""
    try:
        from services.github_service import GitHubService
        print("✓ GitHub service loaded")
    except Exception as e:
        print(f"✗ GitHub service error: {e}")
        return False

    try:
        from services.ai_service import AIService
        print("✓ AI service loaded")
    except Exception as e:
        print(f"✗ AI service error: {e}")
        return False

    try:
        from services.review_engine import ReviewEngine
        print("✓ Review engine loaded")
    except Exception as e:
        print(f"✗ Review engine error: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("AI PR Review Assistant - Installation Test")
    print("=" * 50)
    print()

    results = []

    print("1. Checking Python version...")
    results.append(test_python_version())
    print()

    print("2. Checking dependencies...")
    results.append(test_dependencies())
    print()

    print("3. Checking configuration...")
    results.append(test_config())
    print()

    print("4. Checking services...")
    results.append(test_services())
    print()

    print("=" * 50)
    if all(results):
        print("✓ All checks passed! You can run: python app.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
    print("=" * 50)

    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
