# LeadGen API

B2B lead generation system that extracts local business profiles from Instagram, verifies their emails via SMTP, and exposes the data via a REST API. Designed to integrate directly with N8N for automated proposal sending.

## Stack
- **Backend:** FastAPI, Python 3.11, SQLAlchemy (async)
- **Database:** PostgreSQL
- **Scraping:** Playwright (async)
- **Task Queue:** Celery, Redis

## Setup with Docker
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your variables:
   ```bash
   cp .env.example .env
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
   This will spin up the `api`, `worker`, `beat`, `redis`, `postgres`, and `flower` containers.

## Populate Initial Data
To populate the database with some seed accounts and proxies to start scraping:
```bash
docker-compose exec api python -m seeds.initial_data
```

## API Documentation
Once running, visit:
- **Swagger Documentation:** http://localhost:8000/docs
- **Flower Dashboard:** http://localhost:5555

## N8N Integration
The API provides a dedicated, optimized endpoint for N8N located at `/leads/n8n/daily-batch` (or `/n8n/daily-batch` depending on router config). 

**Requirements for calling N8N Endpoint:**
- HTTP GET
- Set `X-API-Key` header with your `API_KEY` defined in `.env`
- Parameters:
    - `limit` (default 50)
    - `min_score` (default 60)
    - `no_website` (boolean)
    - `mark_as_sent` (boolean)

Example of calling the API from N8N HTTP Request node:
```json
{
  "URL": "http://api:8000/n8n/daily-batch",
  "Method": "GET",
  "Authentication": "None",
  "Headers": {
      "X-API-Key": "your_api_key_here"
  },
  "Query Parameters": {
      "limit": 50,
      "no_website": true
  }
}
```

## AI Proposal Prompt Example
In your N8N flow, you can use the AI node with the following prompt to generate a personalized email:

```text
Eres un experto en ventas B2B que escribe correos en frío altamente personalizados.
El objetivo es ofrecer una página web profesional a un negocio local que no tiene una o tiene una muy mala.

Contexto del prospecto:
- Nombre: {{$json.full_name}}
- Categoría: {{$json.category}}
- Bio de Instagram: {{$json.biography}}
- Información general: {{$json.personalization_context}}

Instrucciones:
1. Sé breve (máximo 4 párrafos cortos).
2. Usa un tono cercano pero profesional.
3. Menciona un dato específico de su perfil para demostrar que no es spam automatizado.
4. El llamado a la acción debe ser agendar una llamada breve de 10 minutos o responder si están interesados.
```
