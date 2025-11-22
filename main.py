import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

app = FastAPI(title="FlamesBlue AI Builder", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="What kind of website to create")
    color: Optional[str] = Field("indigo", description="Tailwind color keyword")
    sections: Optional[int] = Field(3, ge=1, le=6, description="How many sections to include")


class GenerateResponse(BaseModel):
    html: str
    meta: Dict[str, Any]


@app.get("/")
def read_root():
    return {"message": "FlamesBlue AI Builder Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/functions")
def list_functions() -> Dict[str, Any]:
    """Public list of available capabilities (for the UI to render)."""
    functions = [
        {
            "id": "prompt-to-landing",
            "name": "Prompt → Landing Page",
            "description": "Generate a responsive landing page layout from a short idea.",
            "free": True,
        },
        {
            "id": "brand-colors",
            "name": "Brand Colors",
            "description": "Apply a preset accent color across buttons, badges, and highlights.",
            "free": True,
        },
        {
            "id": "hero-3d",
            "name": "3D Hero Animation",
            "description": "Drop in an interactive Spline animation for a futuristic hero.",
            "free": True,
        },
        {
            "id": "feature-grid",
            "name": "Feature Grid",
            "description": "Auto-generate a clean features grid with icons and copy.",
            "free": True,
        },
        {
            "id": "export",
            "name": "One-Click Export",
            "description": "Copy the generated HTML instantly.",
            "free": True,
        },
    ]
    return {"functions": functions}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_site(req: GenerateRequest):
    """Very lightweight site generator. Returns a single-file HTML snippet that uses Tailwind CDN.
    This is free to use and runs without external model dependencies for the demo.
    """
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    color = req.color
    sections = req.sections or 3

    # Simple copy generation from prompt
    title = prompt[:80].rstrip('.')
    if len(title) < len(prompt):
        title += "..."

    # Compose sections
    section_blocks = []
    for i in range(sections):
        section_blocks.append(f"""
        <section class=\"py-16 border-t border-white/10\">
          <div class=\"max-w-6xl mx-auto px-6\">
            <h3 class=\"text-2xl font-semibold text-white mb-4\">Section {i+1}</h3>
            <p class=\"text-slate-300 leading-relaxed\">{prompt} — auto-generated content block {i+1} with responsive layout and accessible typography. Customize freely.</p>
          </div>
        </section>
        """)

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>AI Generated – FlamesBlue</title>
  <script src=\"https://cdn.tailwindcss.com\"></script>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\" />
  <style>body{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial}} .gradient{{background: radial-gradient(1200px 800px at 50% 10%, rgba(99,102,241,.25), transparent), radial-gradient(1000px 600px at 80% 20%, rgba(56,189,248,.2), transparent), radial-gradient(800px 600px at 20% 20%, rgba(244,114,182,.15), transparent)}} .glass{{backdrop-filter:saturate(140%) blur(8px); background:rgba(2,6,23,.55); border:1px solid rgba(255,255,255,.08);}}</style>
</head>
<body class=\"min-h-screen gradient bg-slate-950 text-slate-100\">
  <header class=\"sticky top-0 z-40\">
    <div class=\"max-w-6xl mx-auto px-6 py-4 flex items-center justify-between glass rounded-b-xl\">
      <div class=\"flex items-center gap-3\">
        <div class=\"w-8 h-8 rounded-lg bg-{color}-500/20 border border-{color}-500/30\"></div>
        <span class=\"font-semibold\">FlamesBlue AI</span>
      </div>
      <a href=\"#\" class=\"px-4 py-2 rounded-lg bg-{color}-500 text-white hover:bg-{color}-400 transition\">Get Started</a>
    </div>
  </header>

  <main>
    <section class=\"pt-16 pb-12\">
      <div class=\"max-w-6xl mx-auto px-6 grid md:grid-cols-2 gap-10 items-center\">
        <div>
          <h1 class=\"text-4xl md:text-5xl font-bold leading-tight\">{title}</h1>
          <p class=\"mt-4 text-slate-300\">A modern, responsive page created with FlamesBlue AI. Edit the text, change the colors, and export immediately.</p>
          <div class=\"mt-6 flex gap-3\">
            <a class=\"px-5 py-3 rounded-lg bg-{color}-500 text-white hover:bg-{color}-400 transition\">Primary action</a>
            <a class=\"px-5 py-3 rounded-lg border border-white/10 hover:border-white/20 transition\">Secondary</a>
          </div>
        </div>
        <div class=\"glass rounded-2xl p-6\">
          <div class=\"aspect-video rounded-xl bg-black/30 border border-white/10 flex items-center justify-center text-slate-400\">Media</div>
        </div>
      </div>
    </section>

    {''.join(section_blocks)}

    <footer class=\"py-12 border-t border-white/10 mt-8\">
      <div class=\"max-w-6xl mx-auto px-6 flex items-center justify-between\">
        <span class=\"text-sm text-slate-400\">Generated with FlamesBlue AI</span>
        <a class=\"text-sm text-{color}-400 hover:text-{color}-300\" href=\"#\">Export</a>
      </div>
    </footer>
  </main>
</body>
</html>"""

    return GenerateResponse(
        html=html,
        meta={
            "prompt": prompt,
            "color": color,
            "sections": sections,
        },
    )


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
