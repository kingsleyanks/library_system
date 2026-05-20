# Deploy library_system to Kubernetes

## 1. Build and push the app image

From the [library_system](https://github.com/kingsleyanks/library_system) repo:

```bash
docker build -t kingsleyanks/library_system:latest .
docker push kingsleyanks/library_system:latest
```

## 2. Create secrets (do not commit real values)

**Option A — local file (gitignored)**

```bash
cp Secret.example.yml Secret.yml
# Edit Secret.yml: set django-secret-key, db-password, and database-url
# (password in database-url must match db-password)
kubectl apply -f Secret.yml
```

**Option B — CLI only (nothing sensitive on disk)**

```bash
kubectl create secret generic library-secrets \
  --from-literal=django-secret-key='YOUR_DJANGO_KEY' \
  --from-literal=db-password='YOUR_DB_PASSWORD' \
  --from-literal=database-url='postgres://library_user:YOUR_DB_PASSWORD@library-db:5432/library_db'
```

Only `Secret.example.yml` belongs in git. Never commit `Secret.yml`.

## 3. Apply manifests

```bash
kubectl apply -f PostgresPVC.yml
kubectl apply -f PostgresDeployment.yml
kubectl apply -f PostgresService.yml
kubectl apply -f Deployment.yml
kubectl apply -f Service.yml
```

Skip `kubectl apply -f Secret.yml` if you used Option B and the secret already exists.

## 4. Access the app

```bash
kubectl get svc library-service
```

- **LoadBalancer** (cloud): use `EXTERNAL-IP`.
- **Minikube**: set `type: NodePort` in `Service.yml`, then run `minikube service library-service`.

## Files

| File | In git? |
|------|---------|
| `Secret.example.yml` | Yes (placeholders only) |
| `Secret.yml` | No — listed in `.gitignore` |
| Other `*.yml` manifests | Yes |
