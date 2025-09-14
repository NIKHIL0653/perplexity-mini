# PowerShell setup script for Perplexity AI Clone

Write-Host "🚀 Setting up Perplexity AI Clone..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "⚠️  .env.local file not found. Creating template..." -ForegroundColor Yellow
    
    $envContent = @"
# OpenRouter API Configuration
OPENROUTER_API_KEY=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

# Search API Configuration (optional - for better search results)
# Sign up at https://api.search.brave.com/ for free API key
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
"@
    
    Set-Content -Path ".env.local" -Value $envContent
    Write-Host "✅ Created .env.local with your OpenRouter API key" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start the development server:" -ForegroundColor Cyan
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "📖 Then open http://localhost:3000 in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 For better search results, get a free Brave Search API key:" -ForegroundColor Yellow
Write-Host "   https://api.search.brave.com/" -ForegroundColor White