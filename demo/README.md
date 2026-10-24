# ResidualLab demo

A safe, local-only simulation of the paper's central adapter-residual-risk idea. The three scenarios are synthetic labels; the app never runs shell commands, launches an agent, or touches external systems.

## Run on Windows

```powershell
$env:MODEL_API_KEY = "your Meta Model API key"
python demo/server.py
```

Open http://127.0.0.1:8000. The simulator works without an API key. The **Explain with Muse Spark** button uses Meta Model API model `muse-spark-1.3`; keep the key in your local environment and never commit it. The server binds to localhost.

## Honest scope

This is a hackathon interface prototype, not an experimental result. The activation-monitor panel explicitly reports that a trained probe is not integrated. It does not claim to use or expose Muse Spark activations. Adding an activation probe requires real, labeled action-span data and a validated evaluation; the research protocol is in `../paper/main.tex`.

The explanatory API call receives only one selected synthetic scenario's abstract description. It does not receive benchmark traces or tool outputs.
