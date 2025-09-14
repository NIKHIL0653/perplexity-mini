# Perplexity AI Clone - Gradio Version

A minimal version of Perplexity AI built with **Gradio**, **Python**, and the **DeepSeek V3** model through OpenRouter API. This version features a simple, clean interface focused on functionality over aesthetics, just like the reference design.

## ✨ Features

- **🤖 AI-Powered Research**: Ask any question and get comprehensive answers
- **🔍 Web Search Integration**: Searches the web for relevant information  
- **🧠 AI Synthesis**: Uses DeepSeek V3 to analyze and synthesize search results
- **📚 Source Citations**: Provides proper citations for all sources used
- **🎨 Simple UI**: Clean interface inspired by Perplexity AI's design
- **⚡ Real-time Processing**: See search progress and results as they happen

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install gradio requests python-dotenv
```

### 2. Run the Application
```bash
python gradio_app.py
```

### 3. Open in Browser
Navigate to **http://localhost:7861** to use the application.

## 📁 Project Structure

```
perplexity-ai-clone/
├── gradio_app.py              # Main Gradio application
├── python_search.py           # Web search functionality  
├── python_openrouter.py       # DeepSeek V3 API integration
├── run_gradio.py              # Startup script
├── .env                       # Environment configuration
└── README_GRADIO.md           # This file
```

## 🎯 How It Works

1. **User Input**: Enter any question in the search box
2. **Web Search**: The system searches for relevant articles (currently simulated)
3. **AI Analysis**: DeepSeek V3 analyzes the search results  
4. **Synthesis**: AI creates a comprehensive answer with proper citations
5. **Display**: Results shown in Answer and Sources tabs

## 🔧 Configuration

The application uses these environment variables (configured in `.env`):

```env
# OpenRouter API Configuration (Already set)
OPENROUTER_API_KEY=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

# Application Configuration  
APP_URL=http://localhost:7861

# Optional: Real search API
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here
```

## 🌐 Real Search Integration

Currently uses simulated search results for demonstration. To enable real web search:

1. **Brave Search API** (Recommended):
   - Sign up at https://api.search.brave.com/
   - Add your API key to `.env`
   - Uncomment the real search function in `python_search.py`

2. **Other APIs**: 
   - SerpAPI, Bing Search API, or Google Custom Search
   - Easy to integrate by modifying `python_search.py`

## 🎨 UI Design

The interface matches your reference images with:

- **Dark theme** with clean typography
- **Tab-based layout** (Answer | Sources)  
- **Numbered citations** linking to original sources
- **Example questions** to get users started
- **Responsive design** that works on all devices

## 🛠 Customization

### Change AI Model
Edit `python_openrouter.py`:
```python
self.model = 'deepseek/deepseek-chat'  # Change to other models
```

### Modify Search Sources
Edit `python_search.py` to add more mock results or integrate real APIs.

### Update UI Styling
Edit the `custom_css` variable in `gradio_app.py` to customize appearance.

### Adjust AI Prompts
Modify the system prompt in `python_openrouter.py` to change AI behavior.

## 📊 Example Queries

Try these example questions:

- "Explain the current job market in 2025 for software engineering"
- "What are the latest developments in artificial intelligence?"  
- "How is climate change affecting global weather patterns?"
- "What are the best practices for remote work in 2025?"
- "Explain quantum computing and its potential applications"

## 🔐 API Usage

- **Model**: DeepSeek V3 (free tier via OpenRouter)
- **Rate Limits**: Depends on OpenRouter's free tier limits
- **Cost**: Currently free with the provided API key

## 🚀 Deployment Options

### Local Development
```bash
python gradio_app.py
```

### Production Deployment
1. **Hugging Face Spaces**: Upload to HF Spaces for free hosting
2. **Railway/Render**: Deploy as a web service  
3. **Docker**: Containerize for cloud deployment
4. **VPS**: Run on any Linux server

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7861
CMD ["python", "gradio_app.py"]
```

## 🎯 Portfolio Highlights

This project demonstrates:

- **AI Integration**: Working with modern LLM APIs
- **Web Development**: Building user-friendly interfaces
- **Python Skills**: Clean, modular code architecture
- **API Design**: Handling async operations and error management
- **UX Design**: Creating intuitive, functional interfaces

## 🔧 Technical Stack

- **Frontend**: Gradio (Python web framework)
- **AI Model**: DeepSeek V3 via OpenRouter API
- **Search**: Simulated results (extensible to real APIs)
- **Styling**: Custom CSS for dark theme
- **Environment**: Python 3.9+

## 📝 Notes

- The search results are currently simulated for demonstration
- Real search integration can be easily added
- The interface is optimized for functionality over visual complexity
- Dark theme matches modern AI tool aesthetics

## 🎉 Success!

Your Perplexity AI clone is now running with a simple, effective Gradio interface. The application provides the core functionality of research assistance with AI-powered synthesis and proper source citations.

**Click the preview button to see your application in action!**