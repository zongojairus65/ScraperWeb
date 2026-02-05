import os
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

# Configurer CORS pour autoriser toutes les origines (à ajuster en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de base pour vérifier que l'API fonctionne
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
    # Récupération de la clé API
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        raise HTTPException(
            status_code=500, 
            detail="Clé API Groq manquante. Configurez GROQ_API_KEY dans les variables d'environnement."
        )

    # Configuration du modèle
    graph_config = {
        "llm": {
            "api_key": groq_key,
            "model": "groq/llama3-8b-8192",
        },
        "verbose": False,
        "headless": True,  # Important pour Render (pas de navigateur)
    }

    try:
        # Initialisation et exécution
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )
        
        result = smart_scraper_graph.run()
        
        return {
            "status": "success",
            "url": url,
            "prompt": prompt,
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du scraping: {str(e)}"
        )

# Route spécifique pour les citations (exemple)
@app.get("/citations")
async def get_citations():
    """
    Exemple de route spécifique pour scraper des citations
    """
    return await scrape(
        url="https://example.com/citations",  # À remplacer par votre URL
        prompt="Liste toutes les citations avec leurs auteurs"
    )
