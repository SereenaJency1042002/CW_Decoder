# Intelligent Morse Code Decoder

**Object-Oriented Programming Project — TH Köln, Summer Semester 2026**
**Student:** Sereena Jency

A desktop application that decodes Morse code (CW) into English text — from an uploaded audio file or from a live microphone/radio feed — using digital signal processing, clustering, and two layers of error correction.

---

## What It Does

1. Loads a `.wav`/`.mp3` file, or captures live audio from an input device
2. Finds the tone frequency with FFT and applies a targeted Butterworth bandpass filter
3. Extracts the signal's energy envelope via RMS and converts it to binary ON/OFF using an adaptive threshold
4. Applies **K-Means clustering** to learn dot/dash durations directly from the audio (no fixed timing assumptions)
5. Looks up each dot/dash pattern in the ITU Morse dictionary
6. Runs a **local correction layer** (Hamming distance for unrecognised symbols, Levenshtein distance for garbled words)
7. Runs an **AI correction layer** for context-aware fixes (callsigns, prosigns, ham radio conventions)
8. Displays the waveform, raw decode, and corrected decode in an SDR-style desktop GUI

---

## Architecture

One class per file — each has a single responsibility and can be changed independently.

| Class | File | Responsibility |
|---|---|---|
| `AudioLoader` | `src/audio_loader.py` | Load WAV/MP3 |
| `SignalFilter` | `src/signal_filter.py` | FFT tone detection + Butterworth bandpass |
| `MorseDecoder` | `src/morse_decoder.py` | RMS → K-Means → dictionary lookup → text (used by both file and live decoding) |
| `HMMDecoder` | `src/hmm_decoder.py` | Alternative decoder using a trained Hidden Markov Model — validated against `MorseDecoder` in testing, not currently wired into the app |
| `IntelligentCorrector` | `src/intelligent_corrector.py` | Hamming distance (symbols) + Levenshtein distance (words), always active, fully offline |
| `OfflineAI` | `src/offline_ai.py` | Fine-tuned local T5 model — default AI corrector, works with no internet/API key |
| `AIPredictor` | `src/ai_predictor.py` | Groq-hosted LLaMA 3.3 70B — used instead of `OfflineAI` when a `GROQ_API_KEY` is set |
| `SignalVisualizer` | `src/signal_visualizer.py` | Waveform graph (matplotlib) |
| `LiveDecoder` | `src/live_decoder.py` | Rolling-buffer capture + calibration for live/microphone decoding |
| `UIDisplay` | `src/ui_display.py` | customtkinter GUI |
| `MorseApp` | `main.py` | Entry point — wires everything together |

**File-upload decoding** uses `get_ai()` to pick the AI layer: Groq if `GROQ_API_KEY` is set, otherwise the offline T5 model.
**Live decoding** always uses the offline T5 model (`OfflineAI`), regardless of API key.

---

## Correction Layers

1. **IntelligentCorrector** (always active, offline) — fixes single-symbol errors via Hamming distance and near-miss words via Levenshtein distance, both capped at 1 edit to avoid wrong guesses.
2. **AI layer** (`OfflineAI` or `AIPredictor`) — context-aware pass on top of layer 1: protects callsigns, recognises ham radio conventions (`CQ`, `DE`, `73`, `SK`...), and fills in `?` gaps where context makes the answer unambiguous. Falls back to the uncorrected text silently if it fails.

---

## Known Limitations

- Word-gap detection degrades on noisy real-world audio when the 1:3:7 Morse timing ratio gets compressed.
- The offline T5 model can hallucinate confident-sounding but fabricated text on heavily noisy or out-of-distribution input — a question-mark-ratio guard skips the model above ~25% garbled characters, but doesn't catch all cases.
- MP3 compression introduces spectral noise; results are most reliable with WAV input.

---

## Project Structure

```
CW_Decoder/
├── main.py                    # entry point
├── pyproject.toml             # dependencies
├── src/
│   ├── audio_loader.py
│   ├── signal_filter.py
│   ├── morse_decoder.py
│   ├── hmm_decoder.py
│   ├── intelligent_corrector.py
│   ├── offline_ai.py
│   ├── ai_predictor.py
│   ├── signal_visualizer.py
│   ├── live_decoder.py
│   ├── ui_display.py
│   └── tools/                 # training/testing utilities
│       ├── data_augmentor.py      # builds noisy train/val sets from data/audio_files/
│       ├── generate_training_pairs.py
│       ├── hmm_trainer.py         # trains models/hmm_model.pkl
│       └── batch_tester.py        # scores MorseDecoder vs HMMDecoder → results/batch_report.json
├── models/
│   ├── hmm_model.pkl
│   └── offline_ai_model/      # fine-tuned T5 weights + tokenizer
├── data/
│   ├── audio_files/           # source recordings for training/practice
│   ├── augmented_data/        # noise-augmented train/val split
│   └── morse_training_pairs.csv
├── results/
│   └── batch_report.json      # latest batch_tester.py accuracy report
└── recordings/                # saved live-decode sessions (audio + logs)
```

---

## How to Run

Requires Python 3.11+.

```bash
git clone https://github.com/SereenaJency1042002/CW_Decoder.git
cd CW_Decoder
python -m venv venv
venv\Scripts\activate        # Windows PowerShell
pip install .
python main.py
```

**To enable Groq AI correction** (optional — the app works fully offline without it), create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### Using the app

1. Click **Load Audio File** and select a `.wav`/`.mp3`, or start **Live** decoding
2. Click **Decode**
3. The waveform graph, raw decoded text, and AI-corrected text are shown together

### Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the venv and run `pip install .` |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| AI correction does nothing differently | Offline mode is expected to be conservative; set `GROQ_API_KEY` for the stronger cloud model |
