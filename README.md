# 🎧 DocuSpeak — Document to Audio Converter

Convert **any document** (PDF, DOCX, TXT, EPUB, RTF, images with OCR, and more) to **high-quality AI speech** in **37+ languages** with multiple neural voices.

---

## Architecture

```
docuspeak/
├── backend/               ← Python FastAPI backend
│   ├── main.py            ← REST API (6 endpoints)
│   ├── document_parser.py ← Reads all file formats
│   ├── tts_engine.py      ← Microsoft Neural TTS (edge-tts)
│   ├── requirements.txt   ← Python dependencies
│   └── test_api.py        ← Automated API tests
│
├── flutter_app/           ← Flutter UI (Windows + Web)
│   └── lib/
│       ├── main.dart              ← App entry point
│       ├── screens/
│       │   ├── home_screen.dart   ← File picker + converter
│       │   ├── player_screen.dart ← Audio player with seek
│       │   ├── history_screen.dart← Conversion history
│       │   └── settings_screen.dart
│       ├── services/
│       │   ├── api_service.dart   ← Backend HTTP client
│       │   └── history_service.dart
│       ├── models/history_item.dart
│       └── theme/app_theme.dart   ← Light + Dark theme
│
├── run_docuspeak.bat      ← 🚀 One-click launcher (Windows desktop)
├── run_web.bat            ← 🌐 Web mode launcher (Chrome)
└── start_backend.bat      ← Backend only
```

---

## ✅ Supported File Formats

| Format        | Extension(s)                        | Method          |
|---------------|-------------------------------------|-----------------|
| PDF           | `.pdf`                              | PyMuPDF         |
| Word          | `.docx`, `.doc`                     | python-docx     |
| Plain Text    | `.txt`, `.md`, `.log`, `.csv`       | chardet encoding|
| Rich Text     | `.rtf`                              | striprtf        |
| E-book        | `.epub`                             | EbookLib        |
| Web/Data      | `.html`, `.xml`, `.json`            | chardet          |
| Images (OCR)  | `.png`, `.jpg`, `.bmp`, `.tiff`…    | pytesseract     |

---

## 🗣️ AI Voices (37+ Languages)

Uses **Microsoft Azure Neural Voices** via `edge-tts` (free, no API key needed):

- English (US, UK, India), Hindi, French, German, Spanish, Chinese, Japanese, Korean
- Arabic, Portuguese, Russian, Italian, Dutch, Polish, Turkish, Swedish, Norwegian
- Danish, Finnish, Greek, Hebrew, Thai, Vietnamese, Indonesian, Malay
- Tamil, Telugu, Bengali, Ukrainian, Romanian, Hungarian, Czech, Slovak, Catalan

**Multiple voices per language** (Male/Female options)

---

## 🚀 Quick Start

### Option 1 — Double-click launcher (recommended)

```
Double-click: docuspeak\run_docuspeak.bat
```
This will:
1. Install Python dependencies automatically
2. Start the FastAPI backend
3. Launch the Flutter Windows desktop app

### Option 2 — Web mode (Chrome)

```
Double-click: docuspeak\run_web.bat
```

### Option 3 — Manual commands

**Terminal 1 — Start backend:**
```bash
cd docuspeak/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Run Flutter:**
```bash
cd docuspeak/flutter_app
flutter pub get
flutter run -d windows    # Windows desktop
# OR
flutter run -d chrome     # Web browser
```

---

## 🛠️ Install Dependencies

```bash
# Python backend
pip install -r docuspeak/backend/requirements.txt

# Flutter frontend
cd docuspeak/flutter_app
flutter pub get
```

---

## 🧪 Run Tests

```bash
# Backend API tests
cd docuspeak/backend
python test_api.py

# Flutter analysis
cd docuspeak/flutter_app
flutter analyze
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 Universal Reader | PDF, DOCX, TXT, EPUB, RTF, Images |
| 🎙️ 37+ Languages | Neural AI voices, multiple per language |
| ⚡ Speed Control | 0.5× to 2.0× playback speed |
| 🎵 Pitch Control | ±20 Hz voice pitch adjustment |
| ⏩ Smart Seek | Skip ±10s, full timeline scrubbing |
| 📜 Transcript View | Read original text while listening |
| 🕐 History | Last 50 conversions saved locally |
| 🌙 Dark Mode | Full light/dark theme support |
| 🔄 Live Backend Check | Status indicator with retry |
| 📊 File Info | Shows word count, character count, file size |

---

## 📋 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Backend status check |
| GET | `/voices` | All language + voice options |
| POST | `/parse` | Upload file → extracted text |
| POST | `/synthesize` | Text → MP3 audio stream |
| POST | `/convert` | Upload file → MP3 audio stream |
| POST | `/preview` | Upload file → text preview |
| POST | `/synthesize_b64` | Text → Base64 MP3 (web fallback) |

---

## ⚠️ Notes

- **OCR for images** requires Tesseract to be installed separately:  
  Download from https://github.com/tesseract-ocr/tesseract
- The backend runs locally — no data is sent to any cloud service
- Audio generation requires an internet connection (edge-tts uses Microsoft's servers)
