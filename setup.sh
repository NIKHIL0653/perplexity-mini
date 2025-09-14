#!/bin/bash

echo "🚀 Setting up Perplexity AI Clone..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local file not found. Creating template..."
    cat > .env.local << 'EOF'
# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Search API Configuration (optional - for better search results)
# Sign up at https://api.search.brave.com/ for free API key
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
EOF
    echo "✅ Created .env.local with your OpenRouter API key"
fi

echo "🎉 Setup complete!"
echo ""
echo "🚀 To start the development server:"
echo "   npm run dev"
echo ""
echo "📖 Then open http://localhost:3000 in your browser"
echo ""
echo "💡 For better search results, get a free Brave Search API key:"
echo "   https://api.search.brave.com/"