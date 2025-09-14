#!/usr/bin/env python3 
"""
Real RAG System - Gradio Interface
Mini version of SurfSense that uses the web as database and can analyze documents
"""

import gradio as gr
import os
import re
import time
from dotenv import load_dotenv
from typing import List, Tuple

# Load environment variables
load_dotenv()

# Import our RAG modules
from vector_store import get_rag_system
from python_openrouter import get_openrouter_client, ChatMessage

# =============================
# Custom CSS (Improved Layout)
# =============================
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Helvetica:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

body, .gradio-container {
    background-color: #1a1a1a !important;
    color: #e5e5e5 !important;
    overflow-x: hidden !important;
}

/* Main centered container */
.main-container {
    max-width: 950px;
    margin: 0 auto;
    padding: 20px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

/* Card wrapper */
.card {
    background-color: #1f1f1f;
    border: 1px solid #333333;
    border-radius: 16px;
    padding: 40px 35px;
    width: 100%;
    max-width: 900px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    margin-top: 60px;
}

/* Header */
.logo-text {
    font-size: 42px;
    font-weight: 300;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
    text-align: center;
}

.logo-accent {
    color: #20b2aa;
    font-weight: 500;
}

/* Search input container */
.search-input-container {
    display: flex;
    gap: 8px; /* reduced */
    margin-bottom: 12px; /* reduced */
    align-items: center;
}

/* Search input - longer */
input, textarea {
    background-color: #2a2a2a !important;
    border: 1px solid #404040 !important;
    color: #e5e5e5 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-size: 15px !important;
    flex: 1;
    min-width: 650px; /* wider */
    font-family: 'Segoe UI', sans-serif !important;
}

input:focus, textarea:focus {
    border-color: #20b2aa !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(32, 178, 170, 0.1) !important;
}

input::placeholder, textarea::placeholder {
    color: #888888 !important;
}

/* Square button */
.btn-primary {
    background: linear-gradient(135deg, #20b2aa 0%, #1e9a92 100%) !important;
    border: none !important;
    border-radius: 14px !important; /* more balanced */
    color: white !important;
    font-weight: 500 !important;
    padding: 0 !important;
    font-size: 16px !important;
    transition: all 0.2s ease !important;
    height: 50px !important;
    width: 50px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #1e9a92 0%, #1a8a82 100%) !important;
    transform: translateY(-1px) !important;
}

/* Examples */
.examples-container {
    margin-top: 6px; /* reduced */
    text-align: center;
}

.example-btn {
    background-color: #2a2a2a !important;
    border: 1px solid #404040 !important;
    border-radius: 16px !important;
    color: #cccccc !important;
    padding: 6px 14px !important;
    margin: 3px !important;
    font-size: 12px !important;
    cursor: pointer;
}

.example-btn:hover {
    border-color: #20b2aa !important;
    background-color: #333333 !important;
    color: #e5e5e5 !important;
}

/* Text hierarchy - Enhanced for Perplexity-style formatting */
.content-hierarchy {
    font-family: 'Helvetica', Arial, sans-serif !important;
    line-height: 1.6 !important;
    color: #cccccc !important;
    max-width: 100% !important;
}

.content-hierarchy h1 {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    margin: 0 0 24px 0 !important;
    line-height: 1.3 !important;
    display: block !important;
}

.content-hierarchy h2 {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    margin: 32px 0 16px 0 !important;
    line-height: 1.4 !important;
    display: block !important;
}

.content-hierarchy h3 {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    color: #e5e5e5 !important;
    margin: 24px 0 12px 0 !important;
    line-height: 1.4 !important;
    display: block !important;
}

.content-hierarchy p {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    color: #cccccc !important;
    line-height: 1.7 !important;
    margin: 0 0 20px 0 !important;
    text-align: left !important;
    display: block !important;
}

.content-hierarchy p:last-child {
    margin-bottom: 0 !important;
}

.content-hierarchy strong {
    font-weight: 600 !important;
    color: #ffffff !important;
    font-size: inherit !important;
}

.content-hierarchy em {
    font-style: italic !important;
    color: #d5d5d5 !important;
    font-size: inherit !important;
}

.content-hierarchy ul {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 15px !important;
    color: #cccccc !important;
    margin: 16px 0 24px 0 !important;
    padding-left: 0 !important;
    list-style: none !important;
    line-height: 1.6 !important;
}

.content-hierarchy ol {
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 15px !important;
    color: #cccccc !important;
    margin: 16px 0 24px 20px !important;
    padding-left: 0 !important;
    line-height: 1.6 !important;
}

.content-hierarchy li {
    margin: 12px 0 !important;
    line-height: 1.7 !important;
    color: #cccccc !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
    font-size: 15px !important;
    position: relative !important;
    padding-left: 20px !important;
}

.content-hierarchy ul li:before {
    content: '•' !important;
    color: #20b2aa !important;
    font-weight: bold !important;
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    font-size: 16px !important;
}

/* Answer and Sources tabs - Single unified card */
.answer-content, .sources-content {
    background-color: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
    margin: 0 !important;
    line-height: 1.6 !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
}

/* Unified content container */
.tab-content-wrapper {
    background-color: #1e1e1e !important;
    border: 1px solid #333333 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-top: 20px !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
}

/* Source cards - Enhanced Perplexity-style */
.source-card {
    background-color: #252525 !important;
    border: 1px solid #404040 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin: 8px 0 !important;
    transition: all 0.2s ease !important;
    display: block !important;
}

.source-card:hover {
    border-color: #20b2aa !important;
    background-color: #2a2a2a !important;
    transform: translateY(-1px) !important;
}

.source-title {
    color: #20b2aa !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    text-decoration: none !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
    display: inline-block !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}

.source-title:hover {
    text-decoration: underline !important;
}

.source-domain {
    color: #888888 !important;
    font-size: 12px !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
    margin: 4px 0 8px 0 !important;
    font-weight: 400 !important;
}

.source-snippet {
    color: #cccccc !important;
    font-size: 13px !important;
    margin: 0 !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
    line-height: 1.5 !important;
    font-weight: 400 !important;
}

/* Citation numbers */
.citation-number {
    background: #20b2aa !important;
    color: #fff !important;
    border-radius: 50% !important;
    width: 20px !important;
    height: 20px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    margin-right: 8px !important;
    font-family: 'Helvetica', Arial, sans-serif !important;
}

/* Tabs */
.tab-nav {
    border-bottom: 1px solid #404040 !important;
    background-color: transparent !important;
}

.tab-nav button {
    background-color: transparent !important;
    border: none !important;
    color: #888888 !important;
    font-weight: 400 !important;
    padding: 12px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
    font-family: 'Segoe UI', sans-serif !important;
}

.tab-nav button.selected {
    color: #e5e5e5 !important;
    border-bottom-color: #20b2aa !important;
    font-weight: 500 !important;
}

/* Loading and feedback styles - Minimal */
.loading-container-minimal {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    color: #20b2aa;
    font-family: 'Helvetica', Arial, sans-serif;
}

.loading-header-minimal {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.loading-spinner {
    border: 3px solid #333333;
    border-top: 3px solid #20b2aa;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    margin-right: 12px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.cycling-status {
    font-size: 16px;
    color: #e5e5e5;
    font-family: 'Helvetica', Arial, sans-serif;
    font-weight: 400;
    transition: opacity 0.3s ease;
}

.progress-bar-minimal {
    width: 300px;
    height: 4px;
    background-color: #333333;
    border-radius: 2px;
    overflow: hidden;
    position: relative;
}

.progress-fill-minimal {
    height: 100%;
    background: linear-gradient(90deg, #20b2aa, #1e9a92);
    border-radius: 2px;
    animation: progressSlide 2.5s ease-in-out infinite;
}

@keyframes progressSlide {
    0% { width: 0%; }
    50% { width: 70%; }
    100% { width: 100%; }
}
"""

# =============================
# RAG Logic
# =============================

def format_web_response(query: str, web_results: List, ai_response: str) -> Tuple[str, str, str]:
    """Format web-only results with enhanced text formatting to match Perplexity-style output"""
    
    import re
    
    # Clean up citation numbers first
    formatted_response = ai_response.strip()
    
    # Remove citation numbers like [1], [2], [3][7], etc.
    formatted_response = re.sub(r'\[\d+\](?:\[\d+\])*', '', formatted_response)
    
    # Clean up any double spaces left after removing citations
    formatted_response = re.sub(r'\s+', ' ', formatted_response)
    
    # Convert markdown headers to HTML with proper hierarchy
    formatted_response = re.sub(r'^### (.+?)$', r'<h3>\1</h3>', formatted_response, flags=re.MULTILINE)
    formatted_response = re.sub(r'^## (.+?)$', r'<h2>\1</h2>', formatted_response, flags=re.MULTILINE) 
    formatted_response = re.sub(r'^# (.+?)$', r'<h1>\1</h1>', formatted_response, flags=re.MULTILINE)
    
    # Handle inline headers that weren't caught
    formatted_response = re.sub(r'\s###\s(.+?)(?=\s|$)', r'<h3>\1</h3>', formatted_response)
    
    # Convert markdown formatting
    formatted_response = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted_response)
    formatted_response = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted_response)
    
    # Handle bullet points with improved logic
    # First, find and mark bullet point lines
    lines = formatted_response.split('\n')
    processed_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append('')
            continue
            
        # Check if this is a bullet point
        bullet_match = re.match(r'^[-*•]\s+(.+)$', line)
        if bullet_match:
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(f'<li>{bullet_match.group(1)}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)
    
    # Close any open list
    if in_list:
        processed_lines.append('</ul>')
    
    # Rejoin lines
    formatted_response = '\n'.join(processed_lines)
    
    # Smart paragraph handling - split by double newlines and headers
    parts = re.split(r'(<h[123]>.*?</h[123]>|<ul>.*?</ul>)', formatted_response, flags=re.DOTALL)
    
    processed_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Keep headers and lists as-is
        if re.match(r'^<(h[123]|ul)>', part):
            processed_parts.append(part)
        else:
            # Split text into logical paragraphs
            paragraphs = re.split(r'\n\s*\n', part)
            for para in paragraphs:
                para = para.strip()
                if para and not re.match(r'^<(h[123]|ul|li)', para):
                    processed_parts.append(f'<p>{para}</p>')
                elif para:
                    processed_parts.append(para)
    
    # Join with proper spacing
    formatted_response = '\n\n'.join(processed_parts)
    
    # Final cleanup
    formatted_response = re.sub(r'\n\s*\n', '\n\n', formatted_response)
    
    answer_html = f"""
    <div class="content-hierarchy">
        {formatted_response}
    </div>
    """

    # Enhanced source formatting matching Perplexity style
    sources_html_parts = []
    for i, result in enumerate(web_results):
        # Clean and truncate titles
        title = result.title[:70] + "..." if len(result.title) > 70 else result.title
        snippet = result.snippet[:150] + "..." if len(result.snippet) > 150 else result.snippet
        
        # Extract domain for favicon
        domain = result.domain if hasattr(result, 'domain') else result.url.split('/')[2] if '/' in result.url else result.url
        
        sources_html_parts.append(f"""
        <div class="source-card">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <img src="https://www.google.com/s2/favicons?domain={domain}" 
                     style="width: 16px; height: 16px; margin-right: 8px; border-radius: 2px;" 
                     onerror="this.style.display='none'">
                <a href="{result.url}" target="_blank" class="source-title" style="font-size: 14px; font-weight: 500;">{title}</a>
            </div>
            <div class="source-domain" style="font-size: 12px; color: #888; margin-bottom: 6px;">{domain}</div>
            <div class="source-snippet" style="font-size: 13px; line-height: 1.4;">{snippet}</div>
        </div>
        """)

    sources_html = f"""
    <div class="sources-content">
        {''.join(sources_html_parts) if sources_html_parts else "<p>No sources found.</p>"}
    </div>
    """

    return answer_html, sources_html, ""


def search_web_only(query: str) -> Tuple[str, str, str]:
    """Enhanced web search with more sources and parallel processing"""
    if not query.strip():
        return "Please enter a question.", "No sources.", ""

    try:
        rag_system = get_rag_system()
        # Increased from 3 to 8 results for more comprehensive coverage
        web_results = rag_system.search_web(query, n_results=8)
        
        if not web_results:
            return "No results found.", "", ""

        # Enhanced context preparation with more content but optimized processing
        context_parts = []
        for i, result in enumerate(web_results):
            # Use both snippet and content for richer context, but limit length
            content_preview = result.content[:400] if result.content else result.snippet[:200]
            context_parts.append(f"[{i+1}] {result.title}\nSource: {result.domain}\nContent: {content_preview}")
        context = "\n\n".join(context_parts)

        # Enhanced prompt for better synthesis of multiple sources
        client = get_openrouter_client()
        system_prompt = """You are an expert research assistant that synthesizes information from multiple web sources to provide comprehensive, well-structured answers in the style of Perplexity AI.
        
Key Instructions:
        - Start with a concise introductory paragraph that directly answers the main question
        - Organize information using clear section headers (use ## for main sections)
        - Use bullet points for lists and key details (use - or •)
        - DO NOT include citation numbers like [1], [2], [3] anywhere in your response
        - Write in clear, separate paragraphs with logical flow
        - Use **bold** for emphasis on key terms and concepts
        - Ensure proper paragraph spacing by using double line breaks
        - Focus on the most current and relevant information
        - Present multiple perspectives when sources differ
        - Write in a natural, authoritative tone
        - Structure your response with clear hierarchy: intro paragraph, main sections with headers, detailed explanations
        - Each paragraph should focus on one main concept or idea"""
        
        user_prompt = f"""Question: {query}

Web Sources (analyze all sources for comprehensive coverage):
{context}

Provide a comprehensive, well-structured answer that synthesizes insights from all sources. Use proper headings but do not include citation numbers like [1], [2], etc. Write naturally and cover multiple aspects of the topic."""

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]
        response = client.chat(messages)
        ai_answer = response.content

        return format_web_response(query, web_results, ai_answer)

    except Exception as e:
        return f"Error: {str(e)}", "", ""


# =============================
# UI
# =============================

def create_interface():
    """Create the enhanced interface"""
    with gr.Blocks(css=custom_css, theme=gr.themes.Base(), title="Research Assistant") as demo:
        with gr.Column(elem_classes=["main-container"]):
            with gr.Column(elem_classes=["card"]):
                # Logo
                gr.HTML("""<div class="logo-text">Scout<span class="logo-accent"></span></div>""")

                # Search interface
                with gr.Row(elem_classes=["search-input-container"]):
                    query_input = gr.Textbox(
                        placeholder="Ask anything or mention a source",
                        show_label=False,
                        container=False,
                        lines=1
                    )
                    search_btn = gr.Button("→", elem_classes=["btn-primary"])

                # Example buttons
                gr.HTML("""
                <div class="examples-container">
                    <button class="example-btn" onclick="document.querySelector('textarea').value='Latest AI trends'; document.querySelector('textarea').dispatchEvent(new Event('input'));">Latest AI trends</button>
                    <button class="example-btn" onclick="document.querySelector('textarea').value='Quantum computing'; document.querySelector('textarea').dispatchEvent(new Event('input'));">Quantum computing</button>
                    <button class="example-btn" onclick="document.querySelector('textarea').value='Renewable energy'; document.querySelector('textarea').dispatchEvent(new Event('input'));">Renewable energy</button>
                    <button class="example-btn" onclick="document.querySelector('textarea').value='Medical breakthroughs'; document.querySelector('textarea').dispatchEvent(new Event('input'));">Medical breakthroughs</button>
                </div>
                """)

                # Results area with loading feedback
                question_display = gr.HTML(visible=False)
                loading_display = gr.HTML(visible=False)

                # Unified content container
                with gr.Column(visible=False, elem_classes=["tab-content-wrapper"]) as results_container:
                    results_tabs = gr.Tabs()
                    with results_tabs:
                        with gr.Tab("Answer", elem_classes=["answer-tab"]):
                            answer_output = gr.HTML(elem_classes=["answer-content"])
                        with gr.Tab("Sources", elem_classes=["sources-tab"]):
                            sources_output = gr.HTML(elem_classes=["sources-content"])

        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 30px 0; color: #666666; font-size: 12px; font-family: 'Helvetica', Arial, sans-serif;">
            Powered by DeepSeek V3 via OpenRouter | Web Search via Tavily API
        </div>
        """)

        # Event handlers with enhanced visual feedback
        def handle_search(query):
            if not query.strip():
                return "", gr.update(visible=False), gr.update(visible=False), "", ""

            # Show question and minimal loading indicator
            question_html = f'<div style="font-size: 22px; font-weight: 400; color: #e5e5e5; margin: 30px 0 20px 0; line-height: 1.4; font-family: \'Helvetica\', Arial, sans-serif;">{query}</div>'
            
            # Minimal loading animation with cycling text
            loading_html = f"""
            <div class="loading-container-minimal">
                <div class="loading-header-minimal">
                    <div class="loading-spinner"></div>
                    <span class="cycling-status" id="status-text">Searching the web...</span>
                </div>
                
                <div class="progress-bar-minimal">
                    <div class="progress-fill-minimal"></div>
                </div>
            </div>
            
            <script>
            const statusMessages = [
                "Searching across multiple sources...",
                "Found 8+ sources, analyzing content...",
                "Processing articles and reports in parallel...",
                "Extracting key information...",
                "Cross-referencing multiple perspectives...",
                "Synthesizing comprehensive response..."
            ];
            
            let messageIndex = 0;
            const statusElement = document.getElementById('status-text');
            
            const cycleMessages = () => {{
                if (statusElement) {{
                    statusElement.textContent = statusMessages[messageIndex];
                    messageIndex = (messageIndex + 1) % statusMessages.length;
                }}
            }};
            
            // Start cycling immediately and continue every 1.5 seconds
            cycleMessages();
            const interval = setInterval(cycleMessages, 1500);
            
            // Clean up interval when component unmounts
            setTimeout(() => clearInterval(interval), 30000);
            </script>
            """
            
            return (
                question_html,
                gr.update(visible=True),
                gr.update(visible=True, value=loading_html),
                "",
                ""
            )
        
        def complete_search(query):
            if not query.strip():
                return gr.update(visible=False), "", ""
            
            # Perform the actual search
            answer, sources, _ = search_web_only(query)
            
            return gr.update(visible=False), answer, sources

        # Chain the events for visual feedback
        search_event = search_btn.click(
            handle_search,
            inputs=[query_input],
            outputs=[question_display, results_container, loading_display, answer_output, sources_output]
        ).then(
            complete_search,
            inputs=[query_input],
            outputs=[loading_display, answer_output, sources_output]
        )
        
        submit_event = query_input.submit(
            handle_search,
            inputs=[query_input],
            outputs=[question_display, results_container, loading_display, answer_output, sources_output]
        ).then(
            complete_search,
            inputs=[query_input],
            outputs=[loading_display, answer_output, sources_output]
        )

    return demo


if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not found in environment variables")

    demo = create_interface()
    demo.launch(server_name="127.0.0.1", server_port=7868, share=False, debug=True, show_error=True)
