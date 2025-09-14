#!/usr/bin/env node

// Demo script to test the core functionality
const { searchWeb } = require('./src/lib/search.ts');

async function demo() {
  console.log('🔍 Perplexity AI Clone Demo\\n');
  
  const query = 'What is artificial intelligence?';
  console.log(`Query: ${query}\\n`);
  
  try {
    console.log('Searching web...');
    const results = await searchWeb(query);
    
    console.log(`\\n📊 Found ${results.totalResults} results:\\n`);
    
    results.results.forEach((result, index) => {
      console.log(`[${index + 1}] ${result.title}`);
      console.log(`    ${result.domain}`);
      console.log(`    ${result.snippet.substring(0, 100)}...\\n`);
    });
    
    console.log('✅ Search functionality working!');
    console.log('\\n🚀 To run the full application:');
    console.log('   1. npm run dev');
    console.log('   2. Open http://localhost:3000');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

demo();