# Free Hosting Options

Research for hosting the rally-data-project FastAPI app (Python 3.11+, stateless, ~256 MB RAM, outbound HTTP to rallysimfans.hu).

## Recommended

### 1. Google Cloud Run ⭐
| | |
|---|---|
| **RAM** | 512 MB |
| **Free requests** | 2 million/month |
| **Compute** | ~200 hrs/month at 512 MB |
| **Outbound** | 1 GB/month free |
| **Sleep/cold start** | None (serverless, ~1-2s cold start) |
| **Credit card** | Not required initially |
| **Deployment** | Git push or source-based (auto-containerizes) |

Best overall fit. No spin-down, generous limits, truly free (not a trial). 1 GB outbound covers light scraping — monitor if traffic grows.

### 2. Koyeb
| | |
|---|---|
| **RAM** | 512 MB |
| **CPU** | 0.1 vCPU |
| **Free services** | 1 per org |
| **Credit card** | Not required |
| **Deployment** | Git push |

Simpler than Cloud Run, no credit card needed. Good fallback if GCR setup feels heavy.

### 3. Oracle Cloud Always Free
| | |
|---|---|
| **RAM** | 24 GB (4 OCPU Ampere A1 ARM) |
| **Outbound** | 10 TB/month |
| **Duration** | Never expires |
| **Credit card** | Required for signup |
| **Deployment** | Manual (SSH + Docker/systemd) |

Overkill for this project, but the most powerful and durable option. Worth it if you're comfortable with server admin.

---

## Avoid

| Platform | Reason |
|---|---|
| **Fly.io** | Only 2-hour trial for new accounts — no real free tier |
| **Railway** | 30-day trial then minimum $5/month |
| **Render** | Spins down after 15 min inactivity; free tier status uncertain |
| **Vercel** | Serverless-first, Python support in beta |

---

## Deploying to Google Cloud Run

A minimal `Dockerfile` to add to the project root:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Then deploy:

```bash
gcloud run deploy rally-api --source . --region us-central1 --allow-unauthenticated
```

GCR scales to zero when idle (no cost when unused) and spins back up on the first request.
