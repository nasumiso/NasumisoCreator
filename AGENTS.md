# Repository Guidelines

## Project Structure & Module Organization
Keep work inside the existing layout so assets flow through the LoRA pipeline smoothly:
- `app.py` hosts the Gradio UI and logging setup; UI tabs call helpers from `scripts/`.
- `scripts/` contains preprocessing utilities (`prepare_images.py`, `auto_caption.py`, `add_common_tag.py`) plus shared helpers under `scripts/utils/`.
- `projects/` stores datasets by stage (`1_raw_images`, `2_processed`, `3_tagged`, `lora_models`); never commit raw artwork.
- `config/` holds JSON templates; copy `config.json.example` when customizing paths.
- `docs/`, `.claude/`, and `notebooks/` track specs, plans, and Colab notebooks; update these when workflows change.

## Build, Test, and Development Commands
Use a Python virtualenv under `.venv`:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Start the UI with `./start_nasumiso_trainer.sh` (auto-activates the venv) or `python app.py` for quick iterations; stop with `./stop_nasumiso_trainer.sh`.  
CLI utilities for staged processing:
- `python scripts/prepare_images.py --input .../1_raw_images --output .../2_processed --size 512`
- `python scripts/auto_caption.py --input .../2_processed --output .../3_tagged --threshold 0.35`
- `python scripts/add_common_tag.py --input .../3_tagged --tag nasumiso_style --exclude-jp`

## Coding Style & Naming Conventions
- Python 3.10+, UTF-8 headers, snake_case functions, and upper-case module constants.
- Prefer `pathlib.Path`, type hints, and concise docstrings (Args/Returns in Japanese when user facing).
- Logging goes through `logging.getLogger(__name__)`; surface user-friendly emoji-prefixed messages.
- Keep dependencies in `requirements*.txt`; avoid ad-hoc installs.

## Testing Guidelines
No dedicated test suite; validate changes by running the affected script/UI path against sample data in `projects/nasumiso_v1`.  
When touching WD14 tagging or preprocessing logic, spot-check generated files (image dimensions, `.txt` captions). Document manual verification steps in PR descriptions.

## Commit & Pull Request Guidelines
Follow the existing short-prefix style seen in history (`feat:`, `docs:`, `chore:`) with imperative summaries, optionally mixing JP text for clarity.  
PRs should include:
1. Problem statement and high-level solution.
2. Testing evidence (commands, screenshots of the Gradio tab if UI changes).
3. Any config or doc updates (`README`, `.claude/spec`, `config.json.example`).  
Link relevant issues or tasks and note follow-up work when functionality is partially stubbed.
