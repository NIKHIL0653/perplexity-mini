// Simple web search utility
// For demonstration, this uses a mock search that simulates web search results
// In production, you would integrate with Brave Search API, SerpAPI, or similar

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  domain: string;
}

export interface SearchResponse {
  results: SearchResult[];
  totalResults: number;
}

// Mock search results for demonstration
const mockSearchResults: Record<string, SearchResult[]> = {
  "climate change": [
    {
      title: "Climate Change Evidence and Impacts | NASA",
      url: "https://climate.nasa.gov/effects/",
      snippet: "Climate change is causing measurable changes to Earth's systems. Scientists have been tracking these changes for decades, documenting rising temperatures, melting ice sheets, and changing precipitation patterns.",
      domain: "climate.nasa.gov"
    },
    {
      title: "What is Climate Change? | United Nations",
      url: "https://www.un.org/en/climatechange/what-is-climate-change",
      snippet: "Climate change refers to long-term shifts in temperatures and weather patterns. While climate changes may be natural, since the 1800s, human activities have been the main driver of climate change.",
      domain: "un.org"
    },
    {
      title: "Climate Change Impacts | EPA",
      url: "https://www.epa.gov/climate-impacts",
      snippet: "Climate change impacts human health and wellbeing through more extreme weather events and wildfires, decreased air quality, and diseases transmitted by insects, food, and water.",
      domain: "epa.gov"
    }
  ],
  "artificial intelligence": [
    {
      title: "What is Artificial Intelligence (AI)? | IBM",
      url: "https://www.ibm.com/topics/artificial-intelligence",
      snippet: "Artificial intelligence leverages computers and machines to mimic the problem-solving and decision-making capabilities of the human mind.",
      domain: "ibm.com"
    },
    {
      title: "Artificial Intelligence | Stanford HAI",
      url: "https://hai.stanford.edu/what-ai",
      snippet: "AI is a broad field of computer science concerned with building smart machines capable of performing tasks that typically require human intelligence.",
      domain: "stanford.edu"
    }
  ]
};

export async function searchWeb(query: string): Promise<SearchResponse> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // For demo purposes, return mock results based on keywords
  const lowercaseQuery = query.toLowerCase();
  let results: SearchResult[] = [];
  
  // Check for keyword matches in mock data
  for (const [keyword, mockResults] of Object.entries(mockSearchResults)) {
    if (lowercaseQuery.includes(keyword)) {
      results = [...results, ...mockResults];
    }
  }
  
  // If no specific matches, return generic results
  if (results.length === 0) {
    results = [
      {
        title: `Search Results for "${query}"`,
        url: `https://example.com/search?q=${encodeURIComponent(query)}`,
        snippet: `This is a simulated search result for the query "${query}". In a real implementation, this would be replaced with actual web search results from APIs like Brave Search or SerpAPI.`,
        domain: "example.com"
      },
      {
        title: `${query} - Research and Analysis`,
        url: `https://research.example.com/${query.replace(/\s+/g, '-')}`,
        snippet: `Comprehensive research and analysis on ${query}. This mock result demonstrates how search results would be displayed in the application.`,
        domain: "research.example.com"
      }
    ];
  }
  
  return {
    results: results.slice(0, 10), // Limit to 10 results
    totalResults: results.length
  };
}

// Alternative implementation using Brave Search API (commented out for demo)
/*
export async function searchWebWithBrave(query: string): Promise<SearchResponse> {
  const apiKey = process.env.BRAVE_SEARCH_API_KEY;
  
  if (!apiKey) {
    throw new Error('Brave Search API key not configured');
  }
  
  try {
    const response = await fetch('https://api.search.brave.com/res/v1/web/search', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': apiKey,
      },
      params: {
        q: query,
        count: 10,
        offset: 0,
        mkt: 'en-US',
        safesearch: 'moderate',
        textDecorations: false,
        textFormat: 'Raw'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Search API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    const results: SearchResult[] = data.web?.results?.map((result: any) => ({
      title: result.title || '',
      url: result.url || '',
      snippet: result.description || '',
      domain: new URL(result.url).hostname
    })) || [];
    
    return {
      results,
      totalResults: data.web?.totalEstimatedMatches || results.length
    };
  } catch (error) {
    console.error('Search API error:', error);
    throw error;
  }
}
*/