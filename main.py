import os
from fastapi import FastAPI, HTTPException
from scrapegraphai.graphs import SmartScraperGraph

app = FastAPI()

@app.get("/scrape")
async def scrape(url: str, prompt: str):
    # Récupération sécurisée de la clé API depuis les paramètres du serveur
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        raise HTTPException(status_code=500, detail="Clé API Groq manquante dans la configuration serveur")

    # Configuration utilisant Groq (Llama 3 est gratuit et ultra-rapide)
    graph_config = {
        "llm": {
            "api_key": groq_key,
            "model": "groq/llama3-8b-8192",
        },
        "verbose": False,
    }

    try:
        # Initialisation du scraper
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )

        # Exécution du scraping
        result = smart_scraper_graph.run()
        return {"status": "success", "data": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
