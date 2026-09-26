# CyberGuardian — Screenshot Detection Setup

## Project Structure

```
cyberguardian/
├── screenshot_detection/
│   ├── __init__.py
│   ├── config.py          ← tweak thresholds & model here
│   ├── forensics.py       ← ELA, noise, JPEG ghost
│   ├── ocr_analyzer.py    ← PaddleOCR + scam pattern matching
│   ├── metadata_checker.py← EXIF analysis
│   ├── ui_checker.py      ← paste boundary, font, color anomaly
│   ├── risk_engine.py     ← score aggregation + verdict
│   ├── llm_explainer.py   ← Ollama/Qwen3 explanation
│   └── detector.py        ← main orchestrator
├── main.py                ← FastAPI server
├── test_detector.py       ← CLI test tool
└── requirements.txt
```

---

## Step 1 — Install Dependencies

### PaddlePaddle (GPU — RTX 4050, CUDA 12.x)

```bash
pip install paddlepaddle-gpu==2.6.1.post120 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
```

If that fails or you're on CPU:

```bash
pip install paddlepaddle
```

### Everything else

```bash
pip install -r requirements.txt
```

---

## Step 2 — Make sure Ollama is running with Qwen3

```bash
ollama serve
# In another terminal:
ollama run qwen3:14b
```

CyberGuardian auto-uses Qwen3 for explanations. If Ollama is offline,
it falls back to rule-based explanations automatically — no crash.

---

## Step 3 — Test

```bash
# With your own image:
python test_detector.py path/to/screenshot.png

# With a synthetic test image (auto-created):
python test_detector.py
```

Expected output:
```
RISK SCORE  : 67.4 / 100
VERDICT     : HIGHLY SUSPICIOUS
RISK LEVEL  : HIGH
```

---

## Step 4 — Start FastAPI Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs: http://localhost:8000/docs

---

## API Endpoints

### POST /analyze/screenshot
Upload a file:
```bash
curl -X POST http://localhost:8000/analyze/screenshot \
  -F "file=@fake_upi.jpg"
```

### POST /analyze/screenshot/base64
Send base64 (Flutter-friendly):
```json
{
  "image_base64": "<base64-encoded-bytes>",
  "file_extension": "jpg"
}
```

### Response Format
```json
{
  "risk_score": 72.5,
  "verdict": "HIGHLY SUSPICIOUS",
  "risk_level": "HIGH",
  "color": "#f97316",
  "recommendation": "...",
  "explanation": "AI-generated explanation...",
  "component_scores": {
    "forensic": 80.2,
    "ocr": 60.0,
    "ui": 55.0,
    "metadata": 25.0
  },
  "details": { ... }
}
```

---

## Tuning

Edit `screenshot_detection/config.py`:

- **WEIGHTS** — adjust how much each module contributes to final score
- **THRESHOLDS** — change verdict boundaries
- **ALL_SCAM_KEYWORDS** — add more scam phrases (Hindi/English)
- **OCR_USE_GPU** — set `False` if CUDA issues with PaddleOCR
- **OLLAMA_MODEL** — swap model (e.g., `"llama3:8b"` for faster inference)

---

## Flutter Integration

In your Flutter app, use `http.MultipartRequest`:

```dart
var request = http.MultipartRequest(
  'POST',
  Uri.parse('http://YOUR_IP:8000/analyze/screenshot'),
);
request.files.add(
  await http.MultipartFile.fromPath('file', imagePath),
);
var response = await request.send();
var json = jsonDecode(await response.stream.bytesToString());

// Use json['risk_score'], json['verdict'], json['explanation']
```

Or use the base64 endpoint for cleaner dart code (no multipart needed):

```dart
String b64 = base64Encode(imageBytes);
var response = await http.post(
  Uri.parse('http://YOUR_IP:8000/analyze/screenshot/base64'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'image_base64': b64, 'file_extension': 'jpg'}),
);
```

---

## Known Limitations

- **ELA accuracy** is lower for PNG screenshots (no JPEG compression artifacts to analyze)
- **PaddleOCR** may need extra setup for Hindi (`lang='ch'` + Chinese model downloads Hindi better than `lang='hi'`)
- **Ollama** explanation adds 5–15s latency — disable with `use_llm=False` for faster demo
- **YOLO model** not yet trained — add as a future module once you have labeled UPI screenshot dataset
