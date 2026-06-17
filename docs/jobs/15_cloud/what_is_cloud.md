## Why it exists (THE PROBLEM)

Your model runs on Colab. Colab disconnects after 90 minutes of idle, reboots, kills your session. The trycloudflare URL dies with it. Your model is only alive while YOU are watching the notebook. This is not deployment.

**Cloud deployment** puts your model on a server that runs 24/7, with a stable URL, auto-restart on crash, scaling, and monitoring. Users can access it anytime without you.

The path: Colab prototype → containerize with Docker → deploy to a cloud VM (AWS EC2, GCP Compute Engine, Azure VM) OR a managed ML platform (SageMaker, Vertex AI, HuggingFace Spaces). The VM costs $0.40-2.00/hour for a GPU instance (T4 equivalent). That's $10-50/month for a hobby project, $300-1500/month for production.

## Definition (very simple)

**Cloud deployment strategies for ML (simplest to most complex):**

**Option 1: HuggingFace Spaces (simplest, free tier)**
- Upload model + `app.py` (FastAPI/Gradio)
- HuggingFace runs it, gives you `yourname-cortexcode.hf.space`
- Free for CPU, $0.03/hour for T4 GPU ($21/month)
- Auto-sleep when idle, wakes on request (cold start: 30s)

**Option 2: Single VM + Docker (mid-complexity, most control)**
- Rent a GPU VM (AWS g4dn.xlarge: T4, $0.53/hour, $380/month)
- Install Docker
- `docker run -d --restart=always -p 8000:8000 cortexcode`
- Set up a reverse proxy (nginx) for HTTPS
- Keep it alive with `--restart=always` (auto-restart on crash/reboot)

**Option 3: AWS SageMaker / GCP Vertex AI (production ML)**
- Managed service: upload model, specify instance type, AWS handles rest
- Auto-scaling, monitoring, model registry built in
- More expensive per hour but less ops work
- SageMaker real-time endpoint: $0.53/hr for g4dn.xlarge, plus $0.0016 per endpoint hour

**Option 4: Serverless GPU (Lambda Labs, RunPod, Modal)**
- Pay per second, not per hour
- Cold start: 5-30 seconds (loading model)
- RunPod T4: $0.00012/sec ($0.43/hr), scale-to-zero when idle
- Best for bursty/low-traffic — you pay only when users call

## Practice: Deploying cortexcode to a cloud VM

```bash
# 1. Build Docker image (on your machine or CI)
docker build -t ghcr.io/yourname/cortexcode:latest .
docker push ghcr.io/yourname/cortexcode:latest

# 2. Create VM (AWS CLI example)
aws ec2 run-instances \
    --instance-type g4dn.xlarge \
    --image-id ami-0abcdef1234567890 \  # Deep Learning AMI
    --key-name my-key \
    --security-group-ids sg-0xxx

# 3. SSH into VM
ssh -i my-key.pem ubuntu@<public-ip>

# 4. Pull and run Docker image
docker pull ghcr.io/yourname/cortexcode:latest
docker run -d \
    --name cortexcode \
    --restart=always \
    --gpus all \
    -p 8000:8000 \
    -v /data/models:/app/models \
    ghcr.io/yourname/cortexcode:latest

# 5. Verify
curl http://localhost:8000/health

# 6. Set up nginx for HTTPS (Let's Encrypt)
sudo apt update && sudo apt install nginx certbot python3-certbot-nginx
# ... configure nginx to proxy :8000
# ... certbot to get HTTPS certificate
```

Now your model is at `https://your-domain.com` with auto-restart, auto-HTTPS, accessible 24/7. Deploy cost: $0.53/hour = $380/month. Scale-to-zero option (RunPod/Modal): $0.43/hour while running, $0 while idle. If you have 10 users making 100 requests/day, the model runs for ~5 minutes/day = $0.04/day = $1.20/month.

## Key properties

| Platform | Cost (T4) | Cold start | Auto-scaling | Best for |
|---|---|---|---|---|
| **HF Spaces** | $0.03/hr ($21/mo) | 30s (wake from sleep) | No | Demos, small projects |
| **AWS EC2** | $0.53/hr ($380/mo) | 0s (always on) | Manual | Full control |
| **SageMaker** | $0.53/hr + endpoint fee | 5-10s | Yes (auto) | Production ML |
| **RunPod** | $0.43/hr ($0 idle) | 5-30s | Yes (serverless) | Bursty, low traffic |
| **Modal** | ~$0.50/hr ($0 idle) | 5-15s | Yes (auto) | Python-first, Jupyter |
| **Replicate** | Per-request | 0-30s | Yes (auto) | No infra, just model |

## The Colab-to-Cloud path

```
Colab notebook (prototype)
    ↓
Dockerfile (containerize)
    ↓
docker build + push to GHCR (shareable)
    ↓
HuggingFace Spaces (free demo, 24/7 URL)
    ↓
RunPod / Modal (serverless, pay per use)
    ↓
AWS / GCP VM (production, always-on)
```

Each step adds reliability and cost. HF Spaces is the first upgrade from Colab — $21/month for a T4 that stays alive.

## Common confusion

1. **"Cloud GPU is expensive."** A T4 on AWS: $0.53/hour. Full month: $380. But YOU don't need a full month. A hobby project with 10 users: the model runs for ~10 minutes/day = $0.09/day = $2.70/month on serverless (RunPod). That's cheaper than a coffee. The always-on price is for production traffic.

2. **"I can just keep using Colab."** Colab disconnects after 90 minutes of idle. The tunnel URL expires. You can't auto-restart. If you want a URL that works when you're not watching, you need cloud. Colab is prototyping. Cloud is deployment.

3. **"HuggingFace Spaces is free — why would I use anything else?"** Free tier: CPU only (no GPU), sleeps after inactivity (30s cold start), 16GB disk limit. If your model fits in 16GB and you don't need GPU speed → free. If you need GPU → $0.03/hr. If you need <1s cold start → dedicated VM.

4. **"I need to know AWS/GCP/Azure deeply."** You need: (a) launch a VM with a GPU AMI, (b) SSH in, (c) run Docker. That's 4 commands. The Deep Learning AMIs have CUDA, Docker, and Python pre-installed. You don't need VPC networking, IAM roles, or auto-scaling for a single model.

## Connection to our projects

**cortexcode / logogen:** Build a Dockerfile (we have the list in part 4). Push to GitHub Container Registry. Deploy to HuggingFace Spaces (free CPU, $21/mo GPU). Get a permanent URL. No more "the tunnel died." The model is always at `yourname-cortexcode.hf.space`. Same code. Same model. Different runtime.
