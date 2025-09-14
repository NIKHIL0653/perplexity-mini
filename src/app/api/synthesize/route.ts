import { NextRequest, NextResponse } from 'next/server';
import { getOpenRouterClient } from '@/lib/openrouter';

export async function POST(request: NextRequest) {
  try {
    const { query, searchResults } = await request.json();

    if (!query || !searchResults) {
      return NextResponse.json(
        { error: 'Query and search results are required' },
        { status: 400 }
      );
    }

    // Get the OpenRouter client
    const openRouterClient = getOpenRouterClient();

    // Synthesize the search results with AI
    const answer = await openRouterClient.synthesizeSearchResults(query, searchResults);

    return NextResponse.json({ answer });
  } catch (error) {
    console.error('Synthesis API error:', error);
    
    // Handle specific errors
    if (error instanceof Error) {
      if (error.message.includes('API key not configured')) {
        return NextResponse.json(
          { error: 'OpenRouter API key not configured' },
          { status: 500 }
        );
      }
      
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}