## Why it exists (THE PROBLEM)

Your model runs on your laptop. It doesn't run on your colleague's laptop — wrong Python version, missing CUDA, different OS. It doesn't run in production — no auto-restart on crash, no health checks, no load balancing. It doesn't scale — one machine, one GPU, one user at a time. You can't deploy to 100 users without solving these problems.

**Docker** packages your code + all dependencies into a single image that runs identically everywhere. **Kubernetes** orchestrates many copies of that image across many machines, handling crashes, scaling, networking, and updates.

Together: Docker = "it runs on my machine" → "it runs on any machine." Kubernetes = "one machine" → "a self-healing fleet."

## Definition (very simple)

**Docker container** = a self-contained package with your code, Python, CUDA, PyTorch, model weights, and all dependencies. It's like a lightweight VM that shares the kernel. Anyone with Docker installed can run your model with one command: `docker run cortexcode`.

**Dockerfile** = a recipe for building the container:
```
FROM pytorch/pytorch:2.1.0-cuda12.1    (base image with CUDA+PyTorch)
COPY requirements.txt .                  (copy dependencies list)
RUN pip install -r requirements.txt      (install)
COPY cortexcode/ /app/                   (copy your code)
CMD ["python", "/app/cortexcode_api.py"] (what to run)
```

**Kubernetes** = manages N copies (replicas) of your container across M machines (nodes). If a pod crashes, Kubernetes creates a new one. If traffic spikes, Kubernetes scales up (more replicas). If traffic drops, it scales down.

**Pod** = the smallest unit in K8s: one or more containers sharing network and storage. Typically one container per pod.

**Service** = a stable network endpoint that load-balances across all replicas. Users talk to the service, not individual pods.

## Real-life analogy

**Without Docker:** You hand someone your code and say "run it." They need: Python 3.11, CUDA 12.1, PyTorch 2.1, 47 pip packages, model weights at `/data/cortexcode.pt`, and the right environment variables. Something is always missing.

**With Docker:** You hand them a sealed box with everything inside. They type `docker run cortexcode`. It works. No "it worked on my machine."

**Without Kubernetes:** One server running one copy of your model. Server crashes at 3 AM → model is down until morning. 1000 users at once → server melts. Need to update model → take server offline for 10 minutes (downtime).

**With Kubernetes:** 5 copies running across 3 servers. One server crashes → K8s moves pods to other servers (self-healing). 1000 users → K8s auto-scales to 20 replicas. Update model → rolling update: swap one pod, wait for health, swap next. Zero downtime.

## Tiny numeric example

Scenario: cortexcode model serving 10 requests/minute, can handle 5 concurrent users, deployed on one T4 GPU.

**Without K8s:**
- Deploy one server: `python cortexcode_api.py`
- 50 users: server OOMs (can't handle 50 concurrent). Users get 502 errors.
- Server crashes: manual restart. 5 minutes downtime while you SSH in.
- Model update: `kill -9`, re-pull code, restart. 2 minutes downtime.

**With K8s:**
- Deploy 3 replicas: `kubectl scale deployment cortexcode --replicas=3`
- 50 users: load balancer spreads across 3 replicas. Each handles ~17.
- Server crashes: K8s auto-restarts the pod. ~5 seconds downtime.
- 1000 users: Horizontal Pod Autoscaler (HPA) scales to 10 replicas. Auto.
- Model update: `kubectl rollout restart deployment/cortexcode`. Rolling update. Zero downtime.

## Key properties

| Property | Bare process | Docker + K8s |
|---|---|---|
| Portability | "Works on my machine" | Works everywhere |
| Crash recovery | Manual restart | Automatic (restartCount > 0) |
| Scaling | Manual | Automatic (HPA) |
| Zero-downtime deploy | No | Rolling update |
| Resource isolation | None (one process) | Per-container limits |
| Health checks | No | Liveness + readiness probes |
| Secrets management | Env vars in code | K8s secrets |
| Rollback | Revert commit + restart | `kubectl rollout undo` |

## Minimum K8s deployment for an ML model

```yaml
# cortexcode-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortexcode
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cortexcode
  template:
    metadata:
      labels:
        app: cortexcode
    spec:
      containers:
      - name: cortexcode
        image: ghcr.io/you/cortexcode:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1    # one T4 per replica
          requests:
            nvidia.com/gpu: 1
            memory: "12Gi"
        livenessProbe:            # health check every 30s
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:           # is the model loaded?
          httpGet:
            path: /health
            port: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: cortexcode
spec:
  selector:
    app: cortexcode
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cortexcode-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cortexcode
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

That's the entire production deployment. 40 lines of YAML. Self-healing, auto-scaling, zero-downtime updates.

## Connection to our projects

**cortexcode / logogen:** Write a `Dockerfile`, build the image, push to GitHub Container Registry (free). Anyone with `docker run` can use the model. For production serving, add the K8s YAML above. Deploy on any K8s cluster (GKE, EKS, AKS, or a local `kind` / `minikube` for testing).

**Immediate action:** `docker build -t cortexcode . && docker run -p 8000:8000 cortexcode`. Same as `python cortexcode_api.py` but portable. Serves over the network. Anyone with Docker can test.
