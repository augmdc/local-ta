# local-ta

## Ollama automatic model install

On first run the backend ensures the Ollama server is running and that required models are present.

- Default general LLM: `qwen2.5:7b-instruct`
- Default embedding model: `nomic-embed-text`

You can override via environment variables or `configs/app.yaml` keys:

- Env: `OLLAMA_HOST`, `DEFAULT_MODEL`, `EMBED_MODEL`
- YAML: `ollama_base_url`, `default_model`, `embedding_model`

### One-off ensure via CLI

```bash
./scripts/ensure_ollama.sh --model qwen2.5:7b-instruct --model nomic-embed-text
```

This will start `ollama serve` locally if it is not running, then pull any missing models.

### Backend dev server

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

On startup the app calls the ensure routine; check status at `/health`.