'use client';

import { useState } from 'react';
import { Search, Loader2, ExternalLink } from 'lucide-react';
import { searchWeb, SearchResult } from '@/lib/search';

interface Citation {
  number: number;
  title: string;
  url: string;
  domain: string;
}

interface SearchResponse {
  answer: string;
  citations: Citation[];
  searchResults: SearchResult[];
}

export default function SearchInterface() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // First, get search results
      const searchResults = await searchWeb(query);
      
      // Then, send to our API to synthesize with AI
      const apiResponse = await fetch('/api/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          searchResults: searchResults.results,
        }),
      });

      if (!apiResponse.ok) {
        throw new Error(`API error: ${apiResponse.status}`);
      }

      const data = await apiResponse.json();
      
      // Create citations from search results
      const citations: Citation[] = searchResults.results.map((result, index) => ({
        number: index + 1,
        title: result.title,
        url: result.url,
        domain: result.domain,
      }));

      setResponse({
        answer: data.answer,
        citations,
        searchResults: searchResults.results,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask any question..."
            className="w-full p-4 pr-12 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-500 hover:text-blue-500 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : (
              <Search className="w-6 h-6" />
            )}
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-600 dark:text-red-400">Error: {error}</p>
        </div>
      )}

      {/* Results */}
      {response && (
        <div className="space-y-6">
          {/* AI Answer */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Answer
            </h2>
            <div className="prose dark:prose-invert max-w-none">
              {response.answer.split('\n').map((paragraph, index) => (
                <p key={index} className="mb-3 text-gray-700 dark:text-gray-300 leading-relaxed">
                  {paragraph}
                </p>
              ))}
            </div>
          </div>

          {/* Citations */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Sources
            </h2>
            <div className="space-y-3">
              {response.citations.map((citation) => (
                <div
                  key={citation.number}
                  className="flex items-start space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-sm rounded-full flex items-center justify-center font-medium">
                    {citation.number}
                  </span>
                  <div className="flex-1 min-w-0">
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group"
                    >
                      <div className="flex items-center space-x-2">
                        <h3 className="text-sm font-medium text-blue-600 dark:text-blue-400 group-hover:underline truncate">
                          {citation.title}
                        </h3>
                        <ExternalLink className="w-3 h-3 text-gray-400 flex-shrink-0" />
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {citation.domain}
                      </p>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Searching and analyzing information...
          </p>
        </div>
      )}
    </div>
  );
}