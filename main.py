import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from scrapegraphai.graphs import SmartScraperGraph
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="ScraperWeb API",
    description="API de web scraping avec IA",
    version="1.0.0"
)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Executor pour exécuter le scraper dans un thread séparé
executor = ThreadPoolExecutor(max_workers=3)


def run_scraper(url: str, prompt: str) -> dict:
    """
    Exécute le scraper dans un thread séparé pour éviter
    le conflit avec la boucle asyncio de FastAPI.
    """
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise ValueError("Clé API Groq manquante. Configurez GROQ_API_KEY dans les variables d'environnement.")

    graph_config = {
        "llm": {
            "api_key": groq_key,
            "model": "groq/llama-3.3-70b-versatile",
        },
        "verbose": False,
        "headless": True,
    }

    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )

    return smart_scraper_graph.run()


# Route de base
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur ScraperWeb API",
        "endpoints": {
            "scrape": "/scrape?url=...&prompt=...",
            "docs": "/docs",
            "health": "/health"
        }
    }

# Route de santé
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ScraperWeb"}

# Route principale de scraping
@app.get("/scrape")
async def scrape(
    url: str = Query(..., description="URL à scraper"),
    prompt: str = Query(..., description="Prompt pour l'IA")
):
    """
    Scrape une page web avec l'IA

    Exemple: /scrape?url=https://example.com&prompt=Donne-moi le titre
    """
    try:
        # Exécuter le scraper dans un thread séparé pour éviter
        # le conflit asyncio.run() / boucle d'événements FastAPI
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_scraper, url, prompt)

        return {
            "status": "success",
            "url": url,
            "prompt": prompt,
            "data": result
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scraping: {str(e)}"
    )
