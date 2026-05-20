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
# Edit Secret.yml: set django-secret-key and db-password
kubectl apply -f Secret.yml
```

**Option B — CLI only (nothing sensitive on disk)**

```bash
kubectl create secret generic library-secrets \
  --from-literal=django-secret-key='YOUR_DJANGO_KEY' \
  --from-literal=db-password='YOUR_DB_PASSWORD'
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

## 3.1 If you changed db-password after Postgres was already running

Postgres initializes its user password only on first bootstrap of the data volume. If your `library-db-pvc` already contains data from an older password, app startup can fail with `password authentication failed for user "library_user"`.

For a fresh/dev cluster, recreate the DB volume and pod:

```bash
kubectl delete deployment library-db
kubectl delete pvc library-db-pvc
kubectl apply -f PostgresPVC.yml
kubectl apply -f PostgresDeployment.yml
```

Then restart the app deployment:

```bash
kubectl rollout restart deployment library-app
```

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
