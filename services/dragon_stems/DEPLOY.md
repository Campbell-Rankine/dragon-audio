# Deploying dragon_stems for free

Target: **Hugging Face Spaces, "CPU basic" hardware** — free, no credit card,
2 vCPU / 16 GB RAM / 50 GB (ephemeral) disk. It runs Gradio apps natively, which
is exactly what this service is, and 16 GB is plenty for HDemucs on CPU.

Trade-offs you're accepting:

- **Slow.** Separation runs on 2 CPU cores in float64. Expect roughly real-time
  or slower (a 4-minute song can take several minutes).
- **Sleeps after ~48h without visitors.** The next visit wakes it; cold start is
  a few minutes (container boot + model download).
- **Ephemeral disk.** `output/` is wiped whenever the Space restarts. Download
  stems you want to keep.
- **Public by default.** You can make the Space private for free, then only you
  (logged in) can use it.

## What the Space uses from this folder

| File | Purpose |
| --- | --- |
| `README.md` | YAML header tells Spaces: Gradio SDK, version, `app.py`, Python 3.11 |
| `app.py` | Entry point. Detects Spaces via `SPACE_ID` and skips the share tunnel |
| `requirements.txt` | Python deps. Pulls **CPU-only** torch to keep the image small |
| `packages.txt` | apt packages (`ffmpeg`, a fallback decoder for unusual input formats) |

The `Dockerfile` and `docker-compose.yml` are **not** used by Spaces (Gradio SDK
Spaces build their own image). They're still there for running on your own box.

## One-time setup

1. Create a Hugging Face account: https://huggingface.co/join
2. Create an access token with **write** scope:
   https://huggingface.co/settings/tokens
3. Install the CLI and log in:

   ```bash
   pip install -U huggingface_hub    # provides the `hf` command
   hf auth login                     # paste the write token
   ```

4. Create the Space at https://huggingface.co/new-space:
   - **Space name:** `dragon-stems` (anything works)
   - **SDK:** Gradio
   - **Hardware:** CPU basic · FREE
   - **Visibility:** Public or Private

## Deploy

**NOTE**: Can just push to git

From this folder (`services/dragon_stems`), upload everything except local junk:

```bash
cd services/dragon_stems
hf upload campbell-rankine/spectra-stems . . \
  --repo-type space \
  --exclude ".venv/*" --exclude "output/*" --exclude "**/__pycache__/*" \
  --exclude "*.wav" --exclude "*.mp3"
```

(`--exclude` takes one pattern per flag, so repeat it for each pattern.)

The Space rebuilds automatically on each upload. Watch progress on the Space
page under **Logs → Build**, then **Logs → Container**. The first build takes
~5–10 minutes (installing torch). When it's running you'll see
`Running on local URL: http://0.0.0.0:7860` in the container log.

Open `https://huggingface.co/spaces/campbell-rankine/dragon-stems` and upload
a track.

To redeploy after code changes, run the same `hf upload` command again.

## Optional: auto-deploy from GitHub

The Space is its own git repo, separate from this monorepo. To push on every
change to `main`, add a repo secret `HF_TOKEN` (the write token) in GitHub →
Settings → Secrets → Actions. The workflow lives at
`.github/workflows/deploy-dragon-stems.yml` at the repo root:

```yaml
name: Deploy dragon_stems to HF Spaces
on:
  push:
    branches: [main]
    paths: ["services/dragon_stems/**"]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -U huggingface_hub
      - working-directory: services/dragon_stems
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          hf upload campbell-rankine/dragon-stems . . \
            --repo-type space \
            --exclude ".venv/*" --exclude "output/*" --exclude "**/__pycache__/*" \
            --exclude "*.wav" --exclude "*.mp3"
```

## Troubleshooting

- **Build fails on torch / runs out of disk:** make sure `requirements.txt`
  still has the `--extra-index-url https://download.pytorch.org/whl/cpu` line.
  Without it pip installs the CUDA build (~2.5 GB extra).
- **`ImportError` / `AttributeError` mentioning `HDEMUCS_HIGH_MUSDB_PLUS`:**
  torchaudio ≥ 2.9 removed the model pipelines. Keep `torch==2.8.0` and
  `torchaudio==2.8.0` pinned together.
- **Stuck on "Starting" after waking up:** the first request downloads the
  HDemucs weights (a few hundred MB). Give it a couple of minutes.
- **Two people upload at once:** `app.py` sets the queue concurrency to 1, so
  jobs run one at a time instead of both running out of CPU/RAM.

## Other free options (if Spaces doesn't suit)

| Platform | Free tier | Fit |
| --- | --- | --- |
| **Oracle Cloud Always Free** | ARM VM, 4 cores / 24 GB RAM, always on | Faster and never sleeps. Run `docker compose up`. Sign-up needs a card, and capacity in popular regions can be hard to get |
| **Google Cloud Run** | 2M requests + 360k GiB-s per month | Works with the Dockerfile, but needs a billing account, and you'd add `--memory 8Gi` and a long request timeout |
| Render / Railway / Fly.io | 512 MB RAM or trial credits only | Not enough memory for torch + HDemucs |
