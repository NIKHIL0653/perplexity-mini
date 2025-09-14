#!/usr/bin/env python3
"""
Perplexity AI Clone - Gradio Interface

A sleek, AI-powered research assistant that combines web search with intelligent synthesis.
This application mimics the functionality of Perplexity AI, providing users with comprehensive
answers backed by real-time web sources.

Features:
- Real-time web search integration
- AI-powered answer synthesis using DeepSeek V3
- Beautiful, responsive UI with Perplexity-style design
- Animated loading states with progress feedback
- Citation system with source links
- Dark theme optimized for research sessions

Tech Stack:
- Gradio: Web interface framework
- DeepSeek V3: AI model via OpenRouter API
- Async Python: For smooth user experience
- Custom CSS: Perplexity-inspired styling
"""

import gradio as gr
import asyncio
import time
import os
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any
import html
import random

# Load environment variables
load_dotenv()

# Import our modules
from python_search import search_web, SearchResult
from python_openrouter import get_openrouter_client

# Enhanced CSS for modern, Perplexity-inspired styling
custom_css = """
/* Global dark theme foundation */
.dark {
    background-color: #0a0a0a !important;
    color: #ffffff !important;
}

/* Main container with centered layout */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    background-color: #0a0a0a !important;
    font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Enhanced title styling */
.main-title {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4) !important;
    background-clip: text !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.02em !important;
}

.subtitle {
    color: #9ca3af !important;
    text-align: center !important;
    font-size: 1.1rem !important;
    margin-bottom: 2rem !important;
    font-weight: 400 !important;
}

/* Enhanced input container for longer search bar */
.search-container {
    display: flex !important;
    gap: 12px !important;
    align-items: center !important;
    margin-bottom: 1.5rem !important;
}

.input-container {
    flex: 1 !important;
    min-width: 600px !important;
}

.input-container input {
    background-color: #1a1a1a !important;
    border: 2px solid #333 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-size: 16px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
}

.input-container input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* Square send button with proper alignment */
.btn-send {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border: none !important;
    border-radius: 12px !important;
    width: 56px !important;
    height: 56px !important;
    color: white !important;
    font-size: 20px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    flex-shrink: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.btn-send:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.4) !important;
}

/* Enhanced output container with better visual hierarchy */
.output-container {
    background-color: #111111 !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin: 16px 0 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    line-height: 1.7 !important;
}

.output-container h1 {
    color: #f8fafc !important;
    font-size: 1.75rem !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
    border-bottom: 2px solid #374151 !important;
    padding-bottom: 0.5rem !important;
}

.output-container h2 {
    color: #e2e8f0 !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    margin: 1.5rem 0 0.75rem 0 !important;
}

.output-container h3 {
    color: #cbd5e1 !important;
    font-size: 1.2rem !important;
    font-weight: 500 !important;
    margin: 1.25rem 0 0.5rem 0 !important;
}

.output-container p {
    color: #d1d5db !important;
    margin-bottom: 1rem !important;
    line-height: 1.7 !important;
}

.output-container ul, .output-container ol {
    color: #d1d5db !important;
    margin: 1rem 0 !important;
    padding-left: 1.5rem !important;
}

.output-container li {
    margin-bottom: 0.5rem !important;
    line-height: 1.6 !important;
}

/* Enhanced search status with animated loading */
.search-status {
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 16px 0 !important;
    font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    position: relative !important;
    overflow: hidden !important;
}

.search-status::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent) !important;
    animation: loading-sweep 2s infinite !important;
}

@keyframes loading-sweep {
    0% { left: -100%; }
    100% { left: 100%; }
}

.loading-text {
    color: #3b82f6 !important;
    font-weight: 500 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.loading-dots {
    display: inline-flex !important;
    gap: 2px !important;
}

.loading-dots span {
    width: 4px !important;
    height: 4px !important;
    background-color: #3b82f6 !important;
    border-radius: 50% !important;
    animation: pulse-dot 1.5s infinite !important;
}

.loading-dots span:nth-child(2) {
    animation-delay: 0.2s !important;
}

.loading-dots span:nth-child(3) {
    animation-delay: 0.4s !important;
}

@keyframes pulse-dot {
    0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1); }
}

/* Enhanced citation and source styling */
.citation {
    display: inline-flex !important;
    align-items: center !important;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    border-radius: 50% !important;
    width: 24px !important;
    height: 24px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    justify-content: center !important;
    margin: 0 4px !important;
    text-decoration: none !important;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.2s ease !important;
}

.citation:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4) !important;
}

/* Enhanced source link styling */
.source-link {
    color: #60a5fa !important;
    text-decoration: none !important;
    border-bottom: 1px solid transparent !important;
    margin: 8px 0 !important;
    display: block !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    background-color: rgba(96, 165, 250, 0.05) !important;
    transition: all 0.2s ease !important;
    font-weight: 500 !important;
}

.source-link:hover {
    color: #93c5fd !important;
    background-color: rgba(96, 165, 250, 0.1) !important;
    border-bottom-color: #93c5fd !important;
    transform: translateX(4px) !important;
}

/* Enhanced tabs styling */
.tab-nav {
    background: linear-gradient(135deg, #1e293b, #334155) !important;
    border-bottom: 2px solid #475569 !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 0 8px !important;
}

.tab-nav button {
    background-color: transparent !important;
    color: #94a3b8 !important;
    border: none !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s ease !important;
    margin: 8px 4px 0 4px !important;
}

.tab-nav button:hover {
    color: #e2e8f0 !important;
    background-color: rgba(148, 163, 184, 0.1) !important;
}

.tab-nav button.selected {
    color: #ffffff !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border-bottom: none !important;
    box-shadow: 0 -2px 0 #3b82f6 !important;
}

/* Responsive design improvements */
@media (max-width: 768px) {
    .search-container {
        flex-direction: column !important;
        gap: 16px !important;
    }
    
    .input-container {
        min-width: 100% !important;
    }
    
    .btn-send {
        width: 100% !important;
        height: 48px !important;
    }
    
    .main-title {
        font-size: 2rem !important;
    }
}

/* Enhanced scrollbar styling */
::-webkit-scrollbar {
    width: 8px !important;
}

::-webkit-scrollbar-track {
    background: #1a1a1a !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #374151, #4b5563) !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #4b5563, #6b7280) !important;
}
"""

def format_search_status(current_site: str, completed_sites: List[str], total_sites: int) -> str:
    """
    Creates a visually appealing search status display with progress indicators.
    
    This function formats the current search progress in a human-readable way,
    showing what's being searched right now and what's already been completed.
    It's like having a friendly assistant tell you exactly what's happening
    behind the scenes while you wait for your answer.
    
    Args:
        current_site: The website or source currently being searched
        completed_sites: List of sources that have been successfully searched
        total_sites: Total number of sources to search through
    
    Returns:
        A nicely formatted status string with emojis and progress info
    """
    status_lines = []
    
    # Create an engaging header with loading animation
    status_lines.append('<div class="loading-text">🔍 **Searching the web for you**</div>')
    status_lines.append('<div class="loading-dots"><span></span><span></span><span></span></div>')
    status_lines.append("")
    
    # Show what we're currently working on
    if current_site:
        status_lines.append(f"🔍 Currently exploring: **{current_site}**")
        status_lines.append("")
    
    # Display completed searches with checkmarks
    if completed_sites:
        status_lines.append("**Sources found:**")
        for site in completed_sites:
            status_lines.append(f"✅ {site}")
        status_lines.append("")
    
    # Progress bar visualization
    progress = len(completed_sites) / total_sites if total_sites > 0 else 0
    progress_bar_length = 20
    filled_length = int(progress_bar_length * progress)
    bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
    
    status_lines.append(f"📊 **Progress:** {len(completed_sites)}/{total_sites} sources")
    status_lines.append(f"⏳ {bar} {int(progress * 100)}%")
    
    return "\n".join(status_lines)

def format_reviewing_status(current_idx: int, total_sources: int, current_source: str) -> str:
    """
    Creates an engaging display for the source review phase.
    
    Think of this as your research assistant telling you they're now carefully
    reading through all the articles and websites they found to extract the
    most relevant and accurate information for your question.
    
    Args:
        current_idx: How many sources have been reviewed so far
        total_sources: Total number of sources to review
        current_source: The source currently being analyzed
    
    Returns:
        A formatted status string showing review progress
    """
    status_lines = []
    
    # Eye-catching header with context
    status_lines.append('<div class="loading-text">📚 **Analyzing sources & extracting insights**</div>')
    status_lines.append('<div class="loading-dots"><span></span><span></span><span></span></div>')
    status_lines.append("")
    
    # Show current focus
    if current_source:
        status_lines.append(f"📖 Currently reading: **{current_source}**")
        status_lines.append("")
    
    # Visual progress indicator
    progress = current_idx / total_sources if total_sources > 0 else 0
    progress_bar_length = 15
    filled_length = int(progress_bar_length * progress)
    bar = "📖" * filled_length + "📄" * (progress_bar_length - filled_length)
    
    status_lines.append(f"**Analysis Progress:** {current_idx}/{total_sources} sources")
    status_lines.append(f"📊 {bar}")
    status_lines.append(f"⏳ {int(progress * 100)}% complete")
    
    return "\n".join(status_lines)

def format_sources_display(search_results: List[SearchResult]) -> str:
    """
    Creates a beautiful, user-friendly display of all the sources we found.
    
    Think of this as creating a bibliography for your research - but way more
    engaging than those boring academic ones! Each source gets its own little
    card with a number, title, and domain, making it easy for users to
    explore the original sources if they want to dive deeper.
    
    Args:
        search_results: List of SearchResult objects containing source information
    
    Returns:
        A formatted HTML string with numbered citations and clickable links
    """
    if not search_results:
        return "📝 **No sources found for this query.**\n\nThis might happen if the search didn't return any results. Try rephrasing your question!"
    
    sources_html = []
    sources_html.append("### 📚 Sources & References")
    sources_html.append("*Click any source title to read the full article*")
    sources_html.append("")
    
    for i, result in enumerate(search_results, 1):
        # Create a beautiful numbered citation badge
        citation = f'<span class="citation">{i}</span>'
        
        # Extract domain name for display (remove www. if present)
        domain = result.domain if hasattr(result, 'domain') else result.url.split('/')[2]
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Create an attractive, clickable source link
        source_link = f'<a href="{result.url}" target="_blank" class="source-link">{result.title}</a>'
        
        # Combine everything with nice styling
        sources_html.append(f"{citation} {source_link}")
        sources_html.append(f"<small style='color: #9ca3af; margin-left: 28px; display: block; margin-bottom: 8px;'>🌐 {domain}</small>")
    
    sources_html.append("")
    sources_html.append("*All sources open in a new tab to preserve your research session*")
    
    return "\n".join(sources_html)

async def process_query(query: str, progress=gr.Progress()) -> Tuple[str, str, str]:
    """
    Process a search query with animated progress.
    
    This is an async generator that yields progress updates throughout the search
    and synthesis process, providing real-time feedback to users.
    
    Args:
        query: The user's search question
        progress: Gradio progress tracker for UI updates
        
    Yields:
        Tuple[str, str, str]: (status_message, answer_content, sources_content)
    """
    if not query.strip():
        yield "🔍 Please enter a question to get started!", "", ""
        return
    
    try:
        # Initialize
        progress(0, desc="Initializing search...")
        await asyncio.sleep(0.5)
        
        # Define search sites based on query
        search_sites = [
            "software engineering job market 2025",
            "software engineer hiring trends 2025", 
            "demand for software engineers 2025"
        ]
        
        if "ai" in query.lower() or "artificial intelligence" in query.lower():
            search_sites = [
                "artificial intelligence trends 2025",
                "AI job market 2025",
                "machine learning careers"
            ]
        elif "climate" in query.lower():
            search_sites = [
                "climate change impacts",
                "global warming effects",
                "environmental policy 2025"
            ]
        
        # Enhanced Step 1: Animated Search with Dynamic Messages
        loading_messages = [
            "🔍 Searching the web for the latest information...",
            "🌐 Exploring trusted sources and databases...",
            "📊 Gathering comprehensive data from multiple sites...",
            "🔎 Finding the most relevant and up-to-date content...",
            "📈 Collecting insights from authoritative sources..."
        ]
        
        completed_sites = []
        for i, site in enumerate(search_sites):
            # Show dynamic loading message
            loading_msg = loading_messages[i % len(loading_messages)]
            progress((i + 0.3) / (len(search_sites) + 3), desc=loading_msg)
            
            status = format_search_status(site, completed_sites, len(search_sites))
            yield status, "", ""
            await asyncio.sleep(1.2)  # Slightly longer for better user experience
            
            completed_sites.append(site)
            status = format_search_status("", completed_sites, len(search_sites))
            progress((i + 0.8) / (len(search_sites) + 3), desc=f"✅ Found valuable content from {site}")
            yield status, "", ""
            await asyncio.sleep(0.6)
        
        # Step 2: Perform actual search
        progress(0.7, desc="Gathering search results...")
        search_response = await search_web(query)
        await asyncio.sleep(1)
        
        # Enhanced Step 3: Intelligent Source Analysis Animation
        analysis_messages = [
            "📖 Reading articles and extracting key insights...",
            "🔍 Analyzing content for accuracy and relevance...",
            "💡 Identifying the most important information...",
            "📊 Cross-referencing facts across sources...",
            "🎯 Focusing on what matters most for your question..."
        ]
        
        for i in range(len(search_response.results)):
            current_source = search_response.results[i].domain if i < len(search_response.results) else ""
            analysis_msg = analysis_messages[i % len(analysis_messages)]
            
            status = format_reviewing_status(i + 1, len(search_response.results), current_source)
            progress(0.65 + (i + 1) * 0.2 / len(search_response.results), desc=analysis_msg)
            yield status, "", ""
            await asyncio.sleep(0.9)  # Slightly slower for better perception
        
        # Enhanced Step 4: AI Synthesis with Engaging Messages
        synthesis_messages = [
            "🤖 **Synthesizing information with AI intelligence...**",
            "🧠 **Crafting a comprehensive, well-researched answer...**",
            "✨ **Applying advanced reasoning to your question...**",
            "📝 **Building a clear, informative response...**"
        ]
        
        for i, msg in enumerate(synthesis_messages):
            progress_val = 0.85 + (i + 1) * 0.03
            progress(progress_val, desc=msg.replace('*', '').replace('🤖 ', '').replace('🧠 ', '').replace('✨ ', '').replace('📝 ', ''))
            yield f'<div class="loading-text">{msg}</div><div class="loading-dots"><span></span><span></span><span></span></div>', "", ""
            await asyncio.sleep(0.8)
        
        # Get AI synthesis
        client = get_openrouter_client()
        ai_response = client.synthesize_search_results(query, search_response.results)
        
        # Format sources
        sources_display = format_sources_display(search_response.results)
        
        progress(1.0, desc="Complete!")
        yield "", ai_response, sources_display
        
    except Exception as e:
        # More user-friendly error handling with helpful suggestions
        error_msg = f"🚨 **We encountered an issue while researching your question**\n\n"
                
        if "API" in str(e):
            error_msg += "🔑 This seems to be an API connectivity issue. Please check your internet connection and try again.\n\n"
        elif "timeout" in str(e).lower():
            error_msg += "⏱️ The search took longer than expected. This might be due to high traffic - please try again in a moment.\n\n"
        else:
            error_msg += f"📝 Technical details: {str(e)}\n\n"
                
        error_msg += "💡 **Here are some things you can try:**\n"
        error_msg += "- Rephrase your question in a different way\n"
        error_msg += "- Try a more specific or more general question\n"
        error_msg += "- Check your internet connection\n"
        error_msg += "- Wait a moment and try again\n\n"
        error_msg += "We're continuously working to improve the service. Thank you for your patience! 🙏"
                
        print(f"Detailed error in process_query: {e}")
        yield "", error_msg, ""

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        css=custom_css,
        theme=gr.themes.Base(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
        ).set(
            # Dark theme color scheme - using only supported parameters
            background_fill_primary="#0a0a0a",
            background_fill_secondary="#111111",
            block_background_fill="#1a1a1a",
            input_background_fill="#1a1a1a",
            button_primary_background_fill="#3b82f6",
            button_primary_text_color="#ffffff",
            button_secondary_background_fill="#374151",
            button_secondary_text_color="#e5e7eb",
            # Text colors
            body_text_color="#e5e7eb",
            body_text_color_subdued="#9ca3af",
            block_title_text_color="#f9fafb",
            block_label_text_color="#d1d5db",
        ),
        title="AI Research Assistant - Powered by Advanced AI",
        head="<link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' rel='stylesheet'>"
    ) as demo:
        
        # Enhanced Header with Beautiful Styling
        gr.Markdown(
            """
            <div class="main-title">AI Research Assistant</div>
            <div class="subtitle">Ask any question and get comprehensive, well-researched answers with trusted sources</div>
            """,
            elem_classes=["header"]
        )
        
        # Enhanced Input Area with Improved Layout
        with gr.Row(elem_classes=["search-container"]):
            query_input = gr.Textbox(
                placeholder="What would you like to research today? Ask me anything...",
                label="",
                lines=1,
                max_lines=3,
                scale=10,  # Much larger scale for longer search bar
                elem_classes=["input-container"]
            )
            search_btn = gr.Button(
                "🔍",  # Search icon instead of text
                variant="primary",
                scale=1,  # Small scale for square button
                elem_classes=["btn-send"]
            )
        
        # Status display
        search_status = gr.Markdown(
            "",
            elem_classes=["search-status"],
            visible=True
        )
        
        # Results tabs
        with gr.Tabs() as tabs:
            with gr.Tab("🤖 Answer", elem_id="answer-tab"):
                answer_output = gr.Markdown(
                    "",
                    elem_classes=["output-container"]
                )
            
            with gr.Tab("📚 Sources", elem_id="sources-tab"):
                sources_output = gr.Markdown(
                    "",
                    elem_classes=["output-container"]
                )
        
        # Enhanced Examples with More Engaging Prompts
        gr.Examples(
            [
                "What's the current state of the software engineering job market in 2025?",
                "Explain the breakthrough developments in AI and machine learning this year",
                "How is climate change reshaping global weather patterns and what can we do?",
                "What are the most effective remote work strategies and tools for 2025?",
                "Break down quantum computing: how it works and why it matters for the future",
                "What are the latest trends in renewable energy and sustainability?",
                "Explain the current state of space exploration and upcoming missions"
            ],
            inputs=query_input,
            label="💡 Try these research questions to get started"
        )
        
        # Event handlers
        def handle_search(query):
            """
            Handle search requests with comprehensive error handling and user feedback.
            
            This is the main function that gets called when users click the search button
            or press Enter. It orchestrates the entire search and synthesis process,
            making sure users get helpful feedback at every step.
            
            The function runs asynchronously to prevent the UI from freezing while
            we're doing the heavy lifting of searching the web and processing results.
            """
            def process():
                if not query.strip():
                    return "🔍 Start by typing a question above!", "", ""
                
                try:
                    # Create or get the event loop for async operations
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        # Create a new loop if we're in a different thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run our async search process and collect the final results
                    async def run_process():
                        final_status, final_answer, final_sources = "", "", ""
                        async for status, answer, sources in process_query(query):
                            final_status, final_answer, final_sources = status, answer, sources
                        return final_status, final_answer, final_sources
                    
                    return loop.run_until_complete(run_process())
                    
                except Exception as e:
                    # Provide helpful error messages to users
                    error_msg = f"🚨 **We hit a snag while processing your request!**\n\n"
                    
                    if "network" in str(e).lower() or "connection" in str(e).lower():
                        error_msg += "🌐 It looks like there might be a network connectivity issue.\n"
                        error_msg += "Please check your internet connection and try again.\n\n"
                    elif "api" in str(e).lower():
                        error_msg += "🔑 There seems to be an issue with our AI service.\n"
                        error_msg += "Don't worry, this is usually temporary. Please try again in a moment.\n\n"
                    else:
                        error_msg += f"📝 Error details: {str(e)}\n\n"
                    
                    error_msg += "💡 **Quick fixes to try:**\n"
                    error_msg += "- Refresh the page and try again\n"
                    error_msg += "- Rephrase your question\n"
                    error_msg += "- Wait a minute and retry\n\n"
                    error_msg += "Thanks for your patience! We're working to make this better every day. 🚀"
                    
                    print(f"Error in handle_search: {e}")
                    return "", error_msg, ""
            
            return process()
        
        # Bind events
        search_btn.click(
            handle_search,
            inputs=[query_input],
            outputs=[search_status, answer_output, sources_output]
        )
        
        query_input.submit(
            handle_search,
            inputs=[query_input],
            outputs=[search_status, answer_output, sources_output]
        )
    
    return demo

if __name__ == "__main__":
    """
    Main application entry point.
    
    This is where everything starts! We check that all the necessary
    environment variables are set up, and then launch our beautiful
    research assistant interface.
    
    The application runs on port 7860 by default, making it accessible
    at http://localhost:7860 when you're running it locally.
    """
    
    # Verify that our AI service is properly configured
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  Warning: OPENROUTER_API_KEY not found in environment variables")
        print("📝 Please set it in your .env file or environment variables")
        print("🔑 Without this key, the AI synthesis feature won't work properly")
        print("\n💡 To get started:")
        print("1. Create a .env file in your project directory")
        print("2. Add: OPENROUTER_API_KEY=your_api_key_here")
        print("3. Get an API key from https://openrouter.ai")
    
    print("🚀 Starting AI Research Assistant...")
    print("🌐 The application will be available at http://127.0.0.1:7860")
    print("📚 Ready to help you research any topic with AI-powered insights!")
    
    # Create and launch our research assistant
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",  # Local browser access only
        server_port=7860,         # Standard port for Gradio apps
        share=False,              # Don't create public share link by default
        debug=True,               # Enable debug mode for development
        show_error=True,          # Show detailed error messages
        show_tips=True,           # Show helpful tips to users
        enable_queue=True         # Enable request queuing for better performance
    )