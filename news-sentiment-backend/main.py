from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mlx_lm import load, generate
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5051"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model, tokenizer = load("mlx-community/Llama-3.2-1B-Instruct-4bit")

class AnalysisRequest(BaseModel):
    url: str

def extract_json_from_output(output: str) -> dict:
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            print("Failed to parse JSON from output")
    return None

def sentiment_analysis(headline: str) -> dict:
    instruction_prompt = """
    Analyze the sentiment of the given headline and provide the result in the following JSON format:
    {
        "sentiment": "positive" | "negative" | "neutral",
        "confidence": float (0 to 1),
        "explanation": "brief reason for sentiment",
        "entities": ["relevant categories like 'technology', 'politics', 'health', etc."]
    }
    
    Example:
    {
        "sentiment": "positive",
        "confidence": 0.85,
        "explanation": "Mentions a major technological breakthrough",
        "entities": ["technology", "innovation"]
    }

    Headline: {content}
    """

    prompt = tokenizer.apply_chat_template(
        [
            {"role": "system", "content": instruction_prompt},
            {"role": "user", "content": f"Headline: {headline}"}
        ],
        tokenize=False,
        add_generation_prompt=True,
    )
    result = generate(model, tokenizer, prompt, verbose=True, max_tokens=1024)
    print(extract_json_from_output(result))
    return extract_json_from_output(result)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    parts = path.split('/')
    return ' '.join(part.replace('-', ' ') for part in parts if part).title()

def extract_headline(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different methods to find the headline
        headline = None
        
        # Method 1: Look for h1 tag
        if headline is None:
            h1 = soup.find('h1')
            if h1:
                headline = h1.text.strip()
        
        # Method 2: Look for meta tags
        if headline is None:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                headline = meta_title['content']
        
        # Method 3: Look for title tag
        if headline is None:
            title = soup.find('title')
            if title:
                headline = title.text.strip()
        
        # If we still don't have a headline, normalize the URL
        if headline is None or headline == "":
            headline = normalize_url(url)
        
        return headline
    except Exception as e:
        print(f"Error extracting headline: {e}")
        return normalize_url(url)  # Fallback to normalized URL

def extract_and_summarize_content(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all paragraph texts
        paragraphs = [p.text for p in soup.find_all('p')]
        full_text = ' '.join(paragraphs)
        
        # Modify the prompt to avoid additional phrasing
        summary_instruction = """
        Summarize the following article accurately and concisely. Provide only the summary, with no additional commentary or introductory phrases.
        """
        prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": summary_instruction},
                {"role": "user", "content": full_text}  # Limit input size if needed
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        
        # Generate the summary
        summary_result = generate(model, tokenizer, prompt, verbose=True, max_tokens=1024)
        
        return summary_result.strip()
    except Exception as e:
        print(f"Error extracting and summarizing content: {e}")
        return "Failed to extract and summarize content."



@app.post("/analyze")
async def analyze_sentiment(request: AnalysisRequest):
    try:
        headline = extract_headline(request.url)
        result = sentiment_analysis(headline)
        summary = extract_and_summarize_content(request.url)
        if result:
            return {
                "url": request.url,
                "headline": headline,
                "sentiment": result["sentiment"],
                "explanation": result["explanation"],
                "score": result["confidence"],
                "entities": result["entities"],
                "summary": summary
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to analyze sentiment")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_route():
    return {"message": "Backend is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
