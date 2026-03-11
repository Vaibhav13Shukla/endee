#!/usr/bin/env python3
"""
System Check Script for The Monk AI
Verifies all dependencies and services are running correctly.
"""

import sys
import subprocess
import importlib.util
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        return False, f"Python 3.10+ required, found {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None


def check_venv():
    """Check if running in a virtual environment"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def check_service(url, name):
    """Check if a service is running"""
    try:
        import requests

        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return True, f"{name} is running"
        return False, f"{name} returned status {response.status_code}"
    except Exception as e:
        return False, f"{name} is not accessible: {str(e)[:50]}"


def main():
    print("=" * 60)
    print("The Monk AI - System Status Check")
    print("=" * 60)

    all_passed = True

    # Check Python version
    print("\n📌 Python Version")
    passed, msg = check_python_version()
    print(f"   {'✅' if passed else '❌'} {msg}")
    all_passed = all_passed and passed

    # Check virtual environment
    print("\n📌 Virtual Environment")
    in_venv = check_venv()
    print(f"   {'✅' if in_venv else '⚠️'} Running in virtual environment: {in_venv}")

    # Check key packages
    print("\n📌 Required Packages")
    packages = [
        "fastapi",
        "uvicorn",
        "motor",
        "endee",
        "langchain",
        "sentence_transformers",
        "groq",
        "streamlit",
    ]

    for pkg in packages:
        installed = check_package(pkg)
        print(f"   {'✅' if installed else '❌'} {pkg}")
        all_passed = all_passed and installed

    # Check Endee service
    print("\n📌 Endee Vector Database")
    passed, msg = check_service("http://localhost:8080/health", "Endee")
    print(f"   {'✅' if passed else '❌'} {msg}")

    # Check MongoDB (optional)
    print("\n📌 MongoDB (Optional)")
    passed, msg = check_service("http://localhost:27017", "MongoDB")
    print(f"   {'✅' if passed else '⚠️'} MongoDB: {msg}")

    # Check environment file
    print("\n📌 Environment Configuration")
    env_file = Path(".env")
    if env_file.exists():
        print(f"   ✅ .env file exists")
    else:
        print(f"   ⚠️ .env file not found (create from .env.example)")

    # Check API keys
    print("\n📌 API Keys")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key != "your-groq-api-key-here":
        print(f"   ✅ GROQ_API_KEY is set")
    else:
        print(f"   ❌ GROQ_API_KEY not set (required)")
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All system checks passed!")
    else:
        print("⚠️ Some checks failed. Please review above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
