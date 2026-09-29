# ScamShield AI — Chrome / Chromium Browser Extension & Backend

Proactive suspicious domain and scam detection extension frontend for **ScamShield AI**.

---

## 🛡 Features

- **Netmirror-Inspired UI Structure**:
  - Dark navy cybersecurity theme (`#0a1128`)
  - Crisp high-contrast typography
  - High-visibility red warning panel for detected threats
  - Clean rectangular buttons with subtle borders
  - Compact popup dimensions (~360px × 440px)
  - Zero unnecessary animations or chatbot clutter
- **URL & Domain Analysis**:
  - Automatically extracts and normalizes the active tab's domain (strips `www.`, ports, and internal schemes).
  - Communicates directly with the ScamShield Flask backend via `POST /api/check-url`.
- **Verdict States**:
  - ⚠ **Known Suspicious**: Red alert card displaying risk level (`HIGH`), risk score (e.g. `85/100`), reason, and a critical verification checklist (passwords, OTPs, banking info, personal documents, payments).
  - ✓ **No Known Match**: Neutral status confirming no listing in the dataset, explicitly avoiding false "100% safe" claims.
  - ⚠ **Backend Unavailable**: Clear alert with a retry action if the server cannot be reached.
- **Controls & Navigation**:
  - **[ Pause ] / [ Resume ]**: Temporarily suspend background automated checks (persisted via `chrome.storage.local`).
  - **[ View Full Analysis ]**: Direct deep-link to the ScamShield web analysis page (`http://localhost:5000/analyze?url=<encoded_url>`).
  - **[ Open ScamShield ]**: Navigate to the web application home portal (`http://localhost:5000/`).
  - **[ Scan Current Website ]**: Manual trigger to inspect the current active tab.
  - **⚙ Settings Panel**: In-popup configuration allowing instant changes between backend ports or production URLs.

---

## 📁 Project Structure

```
c:/Users/rhohi/OneDrive/Desktop/fraudlens-ai/extention/
├── extension/
│   ├── manifest.json        # Chrome Manifest V3 configuration
│   ├── popup.html           # Popup UI layout
│   ├── popup.css            # Dark navy cybersecurity styling
│   ├── popup.js             # Tab detection, API query, and UI state controller
│   ├── background.js        # MV3 service worker with automatic checking & badge updates
│   ├── config.js            # Centralized SCAMSHIELD_WEB_URL & SCAMSHIELD_API_URL
│   ├── test_harness.html    # Interactive preview & test sandbox
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── backend/
│   ├── app.py               # Reference Flask backend with POST /api/check-url & web pages
│   ├── dataset.json         # Threat dataset of known suspicious & malicious domains
│   ├── requirements.txt     # Python dependencies (flask)
│   └── test_backend.py      # Automated unit tests for backend API & normalization
└── README.md
```

---

## 🚀 How to Install & Load the Extension in Chrome / Edge / Brave

1. Open your Chromium-based browser (Chrome, Edge, Brave, etc.).
2. Navigate to:
   - Chrome: `chrome://extensions`
   - Edge: `edge://extensions`
   - Brave: `brave://extensions`
3. Enable **Developer mode** (toggle located at the top-right corner).
4. Click **Load unpacked**.
5. Select the `extension/` folder located at:
   ```
   c:\Users\rhohi\OneDrive\Desktop\fraudlens-ai\extention\extension
   ```
6. The **ScamShield AI** extension icon will now appear in your browser toolbar!

---

## ⚡ Starting the Flask Backend

In your terminal or PowerShell:

```bash
# 1. Navigate to backend directory
cd c:\Users\rhohi\OneDrive\Desktop\fraudlens-ai\extention\backend

# 2. (Optional) Install dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python app.py 5000
```

The backend starts listening on `http://127.0.0.1:5000`.

### Verifying with Sample Websites:
- **Known Suspicious**:
  - `https://google-careers-example.xyz/internship`
  - `https://paypal-security-update.xyz/login`
  - `https://example-scam-site.com/internship`
- **No Known Match**:
  - `https://wikipedia.org`
  - `https://github.com`

---

## 🧪 Running Backend Unit Tests

```bash
python test_backend.py
```
Expected output:
```
Ran 4 tests in 0.074s
OK
```
