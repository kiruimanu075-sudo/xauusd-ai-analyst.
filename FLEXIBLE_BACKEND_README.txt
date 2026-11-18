XAUUSD flexible backend + Netlify dashboard

1) Extract/merge these files into your existing xauusd_ai_analyst project.
2) Keep your existing app/market_data.py and app/strategy.py.
3) Ensure app/__init__.py exists.
4) Run locally:
   .\start_backend.ps1
5) Test:
   http://localhost:8000/health
   http://localhost:8000/api/latest
   http://localhost:8000/docs

Netlify:
- Deploy the CONTENTS of the netlify/ folder as a Netlify static site.
- Edit netlify/config.js and replace YOUR-BACKEND with your real backend URL.
- Redeploy the Netlify site after editing config.js.

Render backend:
- Push the project to a GitHub repository.
- Create a Render Web Service connected to that repository.
- Build command: pip install -r requirements.txt
- Start command: uvicorn app.api:app --host 0.0.0.0 --port $PORT
- Root directory: leave blank if app/ and requirements.txt are at repository root.
- Set environment variable NETLIFY_ORIGIN to your actual Netlify site origin, e.g. https://your-site.netlify.app
- Set POLL_SECONDS to 60 if desired.

IMPORTANT:
- Render free web services spin down after 15 minutes without incoming requests and can restart; they are not suitable for guaranteed continuous market polling.
- For continuous backend monitoring while the dashboard is idle, use an always-on paid Render web service or another always-on host.
- Local PowerShell mode runs until Ctrl+C, but Netlify cannot access localhost. Deploy the API to a public HTTPS host for the Netlify dashboard to use it.
- Yahoo Finance XAUUSD data may be delayed, unavailable, or differ from your broker's quote. This is analysis only, not execution.
- This package does not place trades.
