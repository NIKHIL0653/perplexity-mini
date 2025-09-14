#!/usr/bin/env python3
"""
Startup script for Perplexity AI Clone (Gradio Version)
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['gradio', 'requests', 'dotenv']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Please install them with: pip install " + " ".join([p if p != 'dotenv' else 'python-dotenv' for p in missing]))
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Perplexity AI Clone (Gradio Version)...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("""# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Application Configuration
APP_URL=http://localhost:7860

# Search API Configuration (optional)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
""")
        print("✅ Created .env file with your OpenRouter API key")
    
    # Start the application
    print("🌐 Launching Gradio interface...")
    print("📖 Open http://localhost:7860 in your browser")
    
    try:
        # Import and run the app
        from gradio_app import create_interface
        demo = create_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()