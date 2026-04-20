# BharatGraph — Deployment Guide

This document covers every supported way to run BharatGraph. Read only the section that applies to you.

---

## Which deployment is right for you?

| Situation | Go to |
|-----------|-------|
| I want to try it on my laptop | [Personal / Local Setup](#1-personal--local-setup) |
| I want a reproducible setup using Docker | [Docker Setup](#2-docker-setup) |
| I am a developer contributing to the project | [Developer Setup](#3-developer-setup) |
| My organisation wants to deploy this internally | [Organisation / Enterprise Setup](#4-organisation--enterprise-setup) |
| I work for a government department | [Government Deployment](#5-government-deployment) |
| I want to run it on a cloud server | [Cloud Deployment](#6-cloud-deployment) |
| I want to use HuggingFace Spaces (current live deployment) | [HuggingFace Spaces](#7-huggingface-spaces) |

---

## Prerequisites — what you need before starting

### Minimum requirements (for any deployment)

- Python 3.10 or higher
- 4 GB RAM
- 10 GB free disk space
- Internet connection (for scraping live data from government sources)

### Recommended requirements

- Python 3.11
- 8 GB RAM
- 20 GB free disk space
- A text editor (VS Code, Notepad++, etc.)

### What is git and do I need it?

Git is a version control tool. You need it to download the project. It is free.

- **Windows:** Download from https://git-scm.com/download/win and install with default settings.
- **macOS:** Open Terminal and type `git --version`. If not installed, it will prompt you.
- **Linux:** Run `sudo apt install git` or `sudo dnf install git`.

To verify git is installed: open a terminal and type `git --version`. You should see a version number.

---

## 1. Personal / Local Setup

This is for individual use on your own computer — a journalist, researcher, student, or civil society member who wants to investigate on their own machine.

### Step 1: Download the project

Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and run:

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph
```

This downloads the project into a folder called `bharatgraph`.

### Step 2: Create a virtual environment

A virtual environment keeps BharatGraph's dependencies separate from other Python projects on your computer.

**Windows (Command Prompt or Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**macOS or Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt. This means the virtual environment is active.

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

This may take 5–10 minutes. It is downloading all the libraries BharatGraph needs.

### Step 4: Set up environment variables

Environment variables are settings that tell BharatGraph how to connect to its database and data sources.

```bash
cp .env.example .env
```

Now open the `.env` file in a text editor. You will see lines like:

```
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
DATAGOV_API_KEY=your_key
```

**Where to get each value:**

- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Create a free account at https://neo4j.com/cloud/platform/aura-graph-database. Click "New Instance", choose the free tier, and copy the connection URI and password shown after creation.

- `DATAGOV_API_KEY`: Register for a free API key at https://data.gov.in/user/register. After login, find your API key under your profile settings.

- `OPENSANCTIONS_API_KEY`: Free key available at https://opensanctions.org/api. Sign up and copy your key.

All other values are optional. Leave them blank to start — the system will use its built-in sample data.

### Step 5: Load sample data

This loads a small set of example politicians, companies, and contracts so you can try the system immediately without running the full scraper pipeline.

```bash
python -m graph.seed
```

### Step 6: Start the API server

```bash
uvicorn api.main:app --reload
```

You should see output ending with:
```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 7: Open the frontend

Open your file explorer, navigate to the `bharatgraph/frontend/` folder, and double-click `index.html`. The interface will open in your browser.

Alternatively, open your browser and go to `http://127.0.0.1:8000` to access the API directly.

### Step 8: Test that everything works

1. In the search bar, type `Modi` and press Enter. You should see search results.
2. Click on any result to open the entity profile.
3. Click "Investigate" to run the investigation engine.

### Running the full data pipeline

To load live data from all 21+ government sources:

```bash
# Option 1: via command line
python -m processing.pipeline

# Option 2: via HTTP (while the API is running)
curl -X POST http://127.0.0.1:8000/admin/pipeline
```

The pipeline takes 5–15 minutes depending on your internet connection and the responsiveness of external sources.

### Stopping the server

Press `Ctrl + C` in the terminal where the API is running.

---

## 2. Docker Setup

Docker lets you run BharatGraph in a completely isolated container — no Python installation required, and the environment is identical regardless of your operating system.

### Install Docker

- **Windows / macOS:** Download Docker Desktop from https://www.docker.com/products/docker-desktop and install it. Open Docker Desktop and wait for it to say "Docker Desktop is running".
- **Linux:** Run `sudo apt install docker.io docker-compose-plugin` or follow https://docs.docker.com/engine/install/

### Build and run (single container)

```bash
cd bharatgraph

# Copy and edit your environment file first
cp .env.example .env
# Edit .env with your Neo4j credentials (see Step 4 above)

# Build the container image
docker build -t bharatgraph .

# Run it
docker run --env-file .env -p 8000:8000 bharatgraph
```

Open `http://localhost:8000` in your browser.

### Run with Docker Compose (recommended — includes Redis for job queue)

This starts the API, Redis (for the job queue and caching), and automatically restarts on failure:

```bash
docker compose up --build
```

To run in the background:
```bash
docker compose up --build -d
```

To stop:
```bash
docker compose down
```

To see logs:
```bash
docker compose logs -f bharatgraph
```

### Docker Compose services explained

| Service | What it does | Port |
|---------|--------------|------|
| `bharatgraph` | The main API and investigation engine | 8000 |
| `redis` | Job queue and response caching | 6379 (internal) |

### Updating to a new version

```bash
git pull origin main
docker compose down
docker compose up --build -d
```

---

## 3. Developer Setup

For engineers contributing to the codebase.

### Prerequisites

- Python 3.11 (recommended)
- Git
- A code editor with Python support (VS Code recommended)

### Setup

```bash
git clone https://github.com/abinaze/bharatgraph.git
cd bharatgraph

python3.11 -m venv venv
source venv/bin/activate    # Linux/macOS
# or: source venv/Scripts/activate  # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt   # testing + linting tools
python -m spacy download en_core_web_sm

cp .env.example .env
# Edit .env with your credentials
```

### Running tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run a specific module
pytest tests/test_search.py -v

# Run only fast tests (excludes integration tests that need Neo4j)
pytest tests/ -v -m "not integration"
```

### Code style

The project uses Black for formatting and Ruff for linting.

```bash
# Format all Python files
black .

# Check for lint issues
ruff check .

# Fix auto-fixable lint issues
ruff check . --fix
```

### Branch naming

```
feature/phase-N-short-description    # new phase work
fix/short-description                 # bug fixes
docs/description                      # documentation only
```

### Commit message format

```
feat(scope): short description
fix(scope): short description
docs: short description
test: short description
chore: short description
```

Example:
```
feat(search): add semantic similarity ranking via FAISS
fix(investigation): each layer now uses its own Neo4j session
```

---

## 4. Organisation / Enterprise Setup

For companies, NGOs, research institutions, and civil society organisations that want to deploy BharatGraph as an internal tool.

### Architecture overview

```
Internet
    │
    ▼
Reverse Proxy (Nginx / Cloudflare)
    │
    ▼
BharatGraph API (Docker container)
    │           │
    ▼           ▼
Neo4j       Redis
(graph DB)  (queue/cache)
```

### Step 1: Server requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 50 GB SSD | 200 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Docker | 24+ | 24+ |
| Docker Compose | 2.x | 2.x |

### Step 2: Install Docker

```bash
# Ubuntu 22.04
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

Verify: `docker --version` and `docker compose version`

### Step 3: Clone and configure

```bash
git clone https://github.com/abinaze/bharatgraph.git /opt/bharatgraph
cd /opt/bharatgraph
cp .env.example .env
```

Edit `/opt/bharatgraph/.env`:

```env
# Graph database — use your own Neo4j instance for production
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=a_strong_password_here

# API keys
DATAGOV_API_KEY=your_key
OPENSANCTIONS_API_KEY=your_key

# Set your domain
BHARATGRAPH_HOST=https://investigation.yourorganisation.org

# Security
SECRET_KEY=generate_a_random_64_char_string_here
```

To generate a strong SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Set up Neo4j

**Option A — Neo4j AuraDB (cloud, managed)**

1. Go to https://neo4j.com/cloud/platform/aura-graph-database
2. Create an account and a new AuraDB instance
3. Choose Professional tier for production workloads
4. Copy the URI and password to your `.env`

**Option B — Self-hosted Neo4j (recommended for organisations)**

```bash
# Add to your docker-compose.yml (see below)
neo4j:
  image: neo4j:5.18-community
  environment:
    NEO4J_AUTH: neo4j/your_strong_password
    NEO4J_PLUGINS: '["apoc"]'
    NEO4J_dbms_memory_heap_max__size: 4G
  volumes:
    - neo4j_data:/data
  ports:
    - "7474:7474"   # browser UI
    - "7687:7687"   # Bolt protocol
```

### Step 5: Configure Nginx reverse proxy

Create `/etc/nginx/sites-available/bharatgraph`:

```nginx
server {
    listen 80;
    server_name investigation.yourorganisation.org;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name investigation.yourorganisation.org;

    ssl_certificate     /etc/letsencrypt/live/investigation.yourorganisation.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/investigation.yourorganisation.org/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header Strict-Transport-Security "max-age=63072000" always;

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }

    # Frontend static files
    location / {
        root /opt/bharatgraph/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/bharatgraph /etc/nginx/sites-enabled/
sudo nginx -t   # test config
sudo systemctl reload nginx
```

### Step 6: SSL certificate (free via Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d investigation.yourorganisation.org
```

Auto-renewal is set up automatically.

### Step 7: Start the application

```bash
cd /opt/bharatgraph
docker compose up --build -d
```

### Step 8: Seed initial data

```bash
curl -X POST https://investigation.yourorganisation.org/admin/seed
```

### Step 9: Set up automatic data updates

Add a cron job to run the pipeline nightly:

```bash
sudo crontab -e
```

Add:
```
0 2 * * * curl -X POST http://127.0.0.1:8000/admin/pipeline >> /var/log/bharatgraph-pipeline.log 2>&1
```

This runs the full data pipeline at 2:00 AM every night.

### Step 10: Health monitoring

Install UptimeRobot (free) or use your existing monitoring:
- Monitor: `https://investigation.yourorganisation.org/health`
- Expected response: HTTP 200 with `{"status": "ok"}`
- Alert email: your team's operations address

### Backup

```bash
# Backup Neo4j data (if self-hosted)
docker exec neo4j neo4j-admin database dump neo4j --to-path=/var/backup/neo4j/

# Backup application data
tar -czf /var/backup/bharatgraph-$(date +%Y%m%d).tar.gz /opt/bharatgraph/data/
```

### Updating to a new version

```bash
cd /opt/bharatgraph
git pull origin main
docker compose down
docker compose up --build -d
```

---

## 5. Government Deployment

For government departments, regulatory bodies, courts, and intelligence agencies.

### Additional security requirements

Government deployments must meet additional standards. This section covers the security hardening steps required.

### Air-gapped deployment (no internet)

BharatGraph can run in a fully air-gapped environment with no internet access. In this mode, it operates on data already loaded into the graph — no live scraping.

**Step 1: Prepare a deployment package on an internet-connected machine**

```bash
# Export the full repository with all dependencies
pip download -r requirements.txt -d packages/
pip download spacy -d packages/
python -m spacy download en_core_web_sm --direct

# Build a Docker image
docker build -t bharatgraph:offline .
docker save bharatgraph:offline -o bharatgraph-offline.tar
```

**Step 2: Transfer to air-gapped machine**

Copy the following via USB drive or secure file transfer:
- `bharatgraph-offline.tar` (Docker image)
- A Neo4j export file (graph data)
- `.env` with credentials

**Step 3: Load and run on air-gapped machine**

```bash
docker load -i bharatgraph-offline.tar
docker run --env-file .env -p 8000:8000 bharatgraph:offline
```

**Step 4: Import existing graph data**

```bash
curl -X POST http://127.0.0.1:8000/admin/import \
  -F "file=@graph_export.json"
```

### Role-based access control

Configure user roles in `.env`:

```env
ENABLE_AUTH=true
ADMIN_SECRET=a_very_strong_admin_password
```

Three roles are supported:
- `admin` — full access including pipeline trigger and data export
- `analyst` — full read access, investigation, export
- `viewer` — read-only search and profile access

### Audit log compliance

All queries are logged to `logs/audit.jsonl` with SHA-256 hash chaining. This log is tamper-evident — any modification to a past entry breaks the hash chain. For compliance exports:

```bash
# Export audit log for a date range
python -m blockchain.audit_chain --export --from 2024-01-01 --to 2024-12-31 \
  --output audit_export_2024.jsonl
```

### Data residency

All data is stored locally in:
- `data/raw/` — raw scraped records
- `data/processed/` — normalised and merged records
- `logs/` — audit log
- Neo4j database (local or AuraDB)

No data is sent to any third party except:
- Neo4j AuraDB (if using cloud tier) — graph database only
- data.gov.in, cag.gov.in, myneta.info etc. — source data fetches

### Firewall configuration

For a government server, allow only the following outbound connections:

| Destination | Port | Purpose |
|-------------|------|---------|
| `data.gov.in` | 443 | DataGov API |
| `cag.gov.in` | 443 | CAG reports |
| `myneta.info` | 443 | Election affidavits |
| `gem.gov.in` | 443 | GeM contracts |
| `databases.neo4j.io` | 7687 | Neo4j AuraDB (if used) |

Block all other outbound connections from the BharatGraph container.

### Hardened Docker configuration

Add to `docker-compose.yml`:

```yaml
services:
  bharatgraph:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    volumes:
      - ./data:/app/data:rw
      - ./logs:/app/logs:rw
    cap_drop:
      - ALL
    networks:
      - internal_only

networks:
  internal_only:
    internal: true
```

### Incident response

If a security incident is suspected:
1. Stop the container: `docker compose down`
2. Preserve logs: `cp logs/audit.jsonl /secure/backup/`
3. Verify audit chain integrity: `python -m blockchain.audit_chain --verify`
4. Review the last 100 audit entries for anomalies

---

## 6. Cloud Deployment

BharatGraph can be deployed on any cloud provider. Instructions below use general commands that work on AWS, GCP, Azure, DigitalOcean, Hetzner, and any Linux VM.

### Option A: Single VM (simplest)

Provision a Linux VM (Ubuntu 22.04 LTS, 4 vCPU, 8 GB RAM recommended).

SSH into the VM and follow the [Organisation Setup](#4-organisation--enterprise-setup) steps exactly — they are identical for cloud VMs.

### Option B: Managed container service

#### AWS (Elastic Container Service or App Runner)

```bash
# Build and push to ECR
aws ecr create-repository --repository-name bharatgraph
docker build -t bharatgraph .
docker tag bharatgraph:latest 123456789.dkr.ecr.ap-south-1.amazonaws.com/bharatgraph:latest
aws ecr get-login-password | docker login --username AWS --password-stdin \
  123456789.dkr.ecr.ap-south-1.amazonaws.com
docker push 123456789.dkr.ecr.ap-south-1.amazonaws.com/bharatgraph:latest
```

Then create an ECS task definition using the pushed image with the environment variables from `.env`.

#### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/bharatgraph
gcloud run deploy bharatgraph \
  --image gcr.io/YOUR_PROJECT/bharatgraph \
  --platform managed \
  --region asia-south1 \
  --port 8000 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars NEO4J_URI=...,NEO4J_USER=...,NEO4J_PASSWORD=...
```

#### DigitalOcean App Platform

1. Fork the repository to your GitHub account.
2. In DigitalOcean, create a new App from GitHub.
3. Select your fork, branch `main`.
4. Set the Dockerfile as the build method.
5. Add all environment variables from `.env.example` under the App's environment settings.
6. Deploy.

### Option C: Kubernetes

For organisations running Kubernetes clusters (EKS, GKE, AKS):

```yaml
# bharatgraph-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bharatgraph
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bharatgraph
  template:
    metadata:
      labels:
        app: bharatgraph
    spec:
      containers:
        - name: bharatgraph
          image: your-registry/bharatgraph:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: bharatgraph-secrets
          resources:
            requests:
              memory: "2Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
```

Create the secrets:
```bash
kubectl create secret generic bharatgraph-secrets \
  --from-env-file=.env
```

Apply:
```bash
kubectl apply -f bharatgraph-deployment.yaml
```

---

## 7. HuggingFace Spaces

This is the current live deployment at https://abinazebinoly-bharatgraph.hf.space.

### How it works

HuggingFace Spaces uses the `Dockerfile` in the repository root. When you push to `main` on GitHub, a GitHub Actions workflow (`.github/workflows/static.yml`) deploys the frontend to GitHub Pages, and the HuggingFace Space automatically rebuilds from the repository.

### Setting environment secrets on HuggingFace

1. Go to https://huggingface.co/spaces/abinazebinoly/bharatgraph
2. Click "Settings"
3. Under "Repository secrets", add:
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
   - `DATAGOV_API_KEY`
   - `OPENSANCTIONS_API_KEY`

These are injected as environment variables at runtime. They are never visible in logs or the repository.

### Triggering a rebuild

Push any commit to `main`. HuggingFace picks it up within 1–2 minutes and begins rebuilding.

To force a rebuild without a code change:
```bash
git commit --allow-empty -m "chore: trigger HF rebuild"
git push origin main
```

### Checking deployment status

1. Go to the Space URL
2. A banner shows the current build status
3. Check `/health` for API connectivity: `curl https://abinazebinoly-bharatgraph.hf.space/health`

### Cold start behaviour

HuggingFace public Spaces do not cold-start. The container runs continuously. If the Space goes to sleep (very rare on public Spaces), visiting the URL wakes it up within 30 seconds — the frontend's health check retries up to 5 times with exponential backoff to handle this gracefully.

---

## Environment variables reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEO4J_URI` | Yes | Neo4j connection URI | `neo4j+s://1a34e3b8.databases.neo4j.io` |
| `NEO4J_USER` | Yes | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Yes | Neo4j password | `your_strong_password` |
| `DATAGOV_API_KEY` | Recommended | data.gov.in API key | `abc123def456` |
| `OPENSANCTIONS_API_KEY` | Optional | OpenSanctions API key | `xyz789` |
| `GRAPH_ENGINE` | Optional | `neo4j` or `local` (Phase 33+) | `neo4j` |
| `ENABLE_AUTH` | Optional | Enable JWT auth (gov/org) | `false` |
| `ADMIN_SECRET` | If auth enabled | Admin password | 32+ char random string |
| `REDIS_URL` | Optional | Redis for job queue | `redis://localhost:6379` |
| `LOG_LEVEL` | Optional | Logging verbosity | `INFO` |
| `MAX_WORKERS` | Optional | Override auto-detected worker count | `4` |

---

## Troubleshooting

### "NEO4J_URI not set" at startup

Your `.env` file is missing or incorrectly named. Check:
```bash
ls -la | grep .env    # should show .env file
cat .env | head -5    # should show variable assignments
```

### "Neo4j connection failed"

1. Check that your AuraDB instance is running (log in to neo4j.com)
2. Verify the password — AuraDB passwords are case-sensitive
3. Check your internet connection
4. Run the debug endpoint: `curl http://127.0.0.1:8000/debug/neo4j`

### "Search failed. HTTP 500"

Usually means the graph database has no data yet. Run:
```bash
curl -X POST http://127.0.0.1:8000/admin/seed
```

Then search for "Modi" or "Adani".

### Port 8000 already in use

Something else is using port 8000. Either:
- Stop the other application
- Run BharatGraph on a different port: `uvicorn api.main:app --reload --port 8001`
- Then open `http://127.0.0.1:8001` in your browser

### Frontend shows "API not connected"

The API server is not running or is still starting up. The health check retries automatically up to 5 times. Wait 30 seconds. If it still shows disconnected:
1. Check that `uvicorn api.main:app --reload` is running in your terminal
2. Check for error messages in the terminal output

### Docker build fails

Ensure Docker is running:
```bash
docker info   # should show docker system info without errors
```

If it fails with a permissions error on Linux:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Out of memory during pipeline

Reduce the number of parallel workers:
```bash
# Add to .env
MAX_WORKERS=2
```

Or run specific scrapers rather than all at once:
```bash
curl -X POST "http://127.0.0.1:8000/admin/pipeline?scrapers=cag,gem,pib"
```

---

## Security checklist before going to production

- [ ] `.env` file is not committed to git (it is in `.gitignore` by default)
- [ ] NEO4J_PASSWORD is at least 16 characters and randomly generated
- [ ] HTTPS is configured (Let's Encrypt or your certificate)
- [ ] Nginx or another reverse proxy is in front of the API
- [ ] Docker container runs as a non-root user
- [ ] Firewall blocks all ports except 80, 443, and 22
- [ ] `ENABLE_AUTH=true` is set for deployments with sensitive data
- [ ] Audit log at `logs/audit.jsonl` is backed up regularly
- [ ] UptimeRobot or equivalent monitoring is configured

---

## Support and contact

- **Bug reports:** https://github.com/abinaze/bharatgraph/issues
- **Documentation:** https://github.com/abinaze/bharatgraph
- **Live deployment:** https://abinaze.github.io/bharatgraph
- **API:** https://abinazebinoly-bharatgraph.hf.space
