# Perplexity AI Clone

A minimal version of Perplexity AI built with Next.js, TypeScript, and the DeepSeek V3 model through OpenRouter API.

## Features

- **AI-Powered Search**: Ask any question and get comprehensive answers
- **Web Search Integration**: Searches the web for relevant information
- **AI Synthesis**: Uses DeepSeek V3 to analyze and synthesize search results
- **Citations**: Provides proper citations for all sources used
- **Responsive UI**: Clean, simple interface focused on functionality

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
Create a `.env.local` file in the root directory with your API keys:

```env
OPENROUTER_API_KEY=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
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

**Note**: The OpenRouter API key is already configured. For better search results, sign up for a free Brave Search API key at https://api.search.brave.com/

### 3. Run the Development Server
```bash
npm run dev
```

Navigate to http://localhost:3000 to see the application.

## How It Works

1. **User Input**: Enter any question in the search box
2. **Web Search**: The system searches the web for relevant articles
3. **AI Analysis**: DeepSeek V3 analyzes the search results and synthesizes a comprehensive answer
4. **Response**: Get a well-structured answer with proper citations

## Technology Stack

- **Frontend**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS
- **AI Model**: DeepSeek V3 via OpenRouter API
- **Search**: Web search simulation (extensible to real APIs)
- **Icons**: Lucide React

## Current Search Implementation

The current implementation uses simulated search results for demonstration. In production, you can:

1. **Brave Search API**: Uncomment the `searchWebWithBrave` function in `src/lib/search.ts`
2. **SerpAPI**: Integrate with SerpAPI for Google search results
3. **Other APIs**: Easily extensible to other search providers

## File Structure

```
src/
├── app/
│   ├── api/synthesize/route.ts    # API endpoint for AI synthesis
│   └── page.tsx                   # Main page component
├── components/
│   └── SearchInterface.tsx        # Main search interface component
└── lib/
    ├── openrouter.ts             # OpenRouter API integration
    └── search.ts                 # Web search functionality
```

## API Usage

The application uses the OpenRouter API to access DeepSeek V3. The API key provided has access to the free tier of DeepSeek V3.

## Customization

- **Search Provider**: Modify `src/lib/search.ts` to use different search APIs
- **AI Model**: Change the model in `src/lib/openrouter.ts` to use different models
- **UI Styling**: Customize the interface in `src/components/SearchInterface.tsx`
- **System Prompts**: Adjust the AI behavior by modifying prompts in `src/lib/openrouter.ts`

## Deployment

This application can be deployed to Vercel, Netlify, or any platform that supports Next.js applications.

## License

MIT License