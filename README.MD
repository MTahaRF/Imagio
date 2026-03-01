# Imagio

> **AI-powered educational video generator** — type a topic, get a fully rendered, narrated math or science video. No editing. No slides. No effort.

Imagio takes a plain-English topic, runs it through a multi-agent AI pipeline, and produces a narrated Manim animation — complete with voiceover, visual scenes, equations, code walkthroughs, and more. A React-based frontend (currently in development) will make this accessible directly from a browser.

---

## ✨ How It Works

```
Topic (text)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  1. Feasibility Agent  →  Is this a valid science topic? │
│  2. Planner Agent      →  Break into 10 visual scenes    │
│  3. Scene Director     →  Script + fill visual data      │
│  4. Manim Renderer     →  Render each scene to .mp4      │
│  5. Piper TTS          →  Synthesize narration audio     │
│  6. Merger             →  Stitch into one final video    │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
Imagio/
├── src/
│   ├── agents/
│   │   ├── feasibility.py       # Validates topic + builds curriculum
│   │   ├── planner.py           # Assigns templates to each scene
│   │   ├── scene_director.py    # Writes script + fills template data
│   │   ├── scripter.py          # (legacy) narration writer
│   │   └── coder.py             # (legacy) JSON → Manim code
│   ├── templates/
│   │   ├── base.py              # Abstract base for all templates
│   │   ├── registry.py          # Auto-registers all templates
│   │   ├── title_slide.py
│   │   ├── bullet_points.py
│   │   ├── definition_slide.py
│   │   ├── equation_transform.py
│   │   ├── code_walkthrough.py
│   │   ├── graph_plot.py
│   │   ├── split_slide.py
│   │   ├── comparison_slide.py
│   │   ├── picture_slide.py
│   │   └── blank.py
│   ├── tools/
│   │   ├── manim_runner.py      # Renders .py files via Manim CLI
│   │   ├── merger.py            # FFmpeg scene stitcher
│   │   ├── tts.py               # Standalone Piper TTS
│   │   └── cleanup.py           # Post-run file cleanup
│   ├── services/
│   │   └── piper_service.py     # Manim-Voiceover TTS integration
│   ├── languages.py             # Language configs (en, es, fr, hi)
│   ├── config.py                # API keys, paths, model configs
│   ├── prompts.py               # All LLM system prompts
│   └── llm_client.py            # LLM provider abstraction
├── frontend/                    # React frontend (in development)
├── workspace/
│   ├── code/                    # Generated scene .py files
│   └── media/                   # Rendered videos + final output
├── voices/                      # Piper .onnx voice models
├── pipeline.py                  # Core pipeline entry point
├── test_pipeline.py             # CLI test harness
├── sample_test.py               # Template unit tests
├── download_models.py           # One-shot Piper model downloader
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/imagio.git
cd imagio
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
NEBIUS_API_KEY=your_nebius_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### 5. Install system dependencies

| Dependency | Purpose | Install |
|---|---|---|
| [Manim](https://docs.manim.community/en/stable/installation.html) | Animation renderer | `pip install manim` |
| [FFmpeg](https://ffmpeg.org/download.html) | Video merging | Add to system PATH |
| [Piper TTS](https://github.com/rhasspy/piper) | Offline voice synthesis | `pip install piper-tts` |
| [pydub](https://github.com/jiaaro/pydub) | WAV → MP3 conversion | `pip install pydub` |

### 6. Download voice models

```bash
# Download all 4 languages (en, es, fr, hi)
python download_models.py

# Or download a single language
python download_models.py --lang en
python download_models.py --lang hi
```

---

## 🚀 Running the Pipeline

### Basic run

```bash
python test_pipeline.py --topic "How does gravity work"
```

### With language selection

```bash
# English (default)
python test_pipeline.py --topic "Factorizing x squared plus 5x plus 6"

# French
python test_pipeline.py --topic "Factorizing x squared plus 5x plus 6" --language fr

# Hindi
python test_pipeline.py --topic "Factorizing x squared plus 5x plus 6" --language hi

# Spanish
python test_pipeline.py --topic "Factorizing x squared plus 5x plus 6" --language es
```

### All available flags

| Flag | Description |
|---|---|
| `--topic` | The educational topic to generate a video for |
| `--language` | Output language: `en` \| `es` \| `fr` \| `hi` (default: `en`) |
| `--dry-run` | Run LLM steps only — skip Manim rendering |
| `--no-merge` | Render scenes individually, skip final concatenation |
| `--no-cleanup` | Keep all intermediate files after the run |


---

## 🌐 Supported Languages

| Code | Language | TTS Model |
|---|---|---|
| `en` | English | `en_US-lessac-medium` |
| `es` | Español | `es_ES-mls_10246-low` |
| `fr` | Français | `fr_FR-siwis-medium` |
| `hi` | हिन्दी | `hi_IN-priyamvada-medium` |

---

## 🎨 Available Templates

| Template | Best Used For |
|---|---|
| `title_slide` | Opening scene with title and subtitle |
| `bullet_points` | Key concepts, summaries, lists of facts |
| `definition_slide` | Term definitions with formula and example |
| `equation_transform` | Step-by-step equation derivations |
| `code_walkthrough` | Annotated code with line-by-line highlights |
| `graph_plot` | Function graphs and plots |
| `split_slide` | Side-by-side diagram + explanation |
| `comparison_slide` | Two-column comparisons |
| `picture_slide` | Image with caption and body text |
| `blank` | Custom raw Manim code |

---

## 🖥️ Frontend

A React-based frontend is being built to allow users to:

- Enter a topic and language from a browser
- Track pipeline progress in real time
- Preview and download the generated video

The frontend will communicate with a FastAPI backend that wraps `pipeline.py`. Stay tuned.

## Youtube Link of Imagio:
https://youtu.be/Xi_Obv8EdmQ
[![Imagio Demo Video](https://youtu.be/Xi_Obv8EdmQ/0.jpg)](https://youtu.be/Xi_Obv8EdmQ)
---

## 📄 License

MIT License — see `LICENSE` for details.