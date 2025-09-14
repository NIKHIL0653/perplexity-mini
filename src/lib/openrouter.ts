// OpenRouter API integration for DeepSeek V3 model

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class OpenRouterClient {
  private apiKey: string;
  private baseUrl = 'https://openrouter.ai/api/v1';
  private model = 'deepseek/deepseek-chat'; // DeepSeek V3 model

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async chat(messages: ChatMessage[]): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
          'X-Title': 'Perplexity AI Clone'
        },
        body: JSON.stringify({
          model: this.model,
          messages,
          temperature: 0.7,
          max_tokens: 2000,
          stream: false
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`OpenRouter API error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
      }

      const data = await response.json();
      
      if (!data.choices || data.choices.length === 0) {
        throw new Error('No response generated from the model');
      }

      return {
        content: data.choices[0].message.content,
        usage: data.usage
      };
    } catch (error) {
      console.error('OpenRouter API error:', error);
      throw error;
    }
  }

  async synthesizeSearchResults(query: string, searchResults: any[]): Promise<string> {
    const systemPrompt = `You are an AI research assistant that synthesizes information from web search results to provide comprehensive, accurate answers. Your task is to:

1. Analyze the provided search results
2. Extract the most relevant and accurate information
3. Synthesize a comprehensive answer that addresses the user's question
4. Maintain objectivity and cite sources appropriately
5. If there are conflicting information, mention the different perspectives
6. Keep the response concise but thorough

Format your response in a clear, well-structured manner with proper citations using [1], [2], etc. that correspond to the source URLs provided.`;

    const searchContext = searchResults.map((result, index) => 
      `[${index + 1}] ${result.title}\nURL: ${result.url}\nContent: ${result.snippet}\n`
    ).join('\n');

    const userPrompt = `Question: ${query}

Search Results:
${searchContext}

Please provide a comprehensive answer based on these search results. Include relevant citations using the format [1], [2], etc.`;

    const messages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ];

    const response = await this.chat(messages);
    return response.content;
  }
}

// Singleton instance for use across the application
let openRouterClient: OpenRouterClient | null = null;

export function getOpenRouterClient(): OpenRouterClient {
  if (!openRouterClient) {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      throw new Error('OpenRouter API key not configured');
    }
    openRouterClient = new OpenRouterClient(apiKey);
  }
  return openRouterClient;
}