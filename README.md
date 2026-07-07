# Saarthi — AI Wealth Avatar

**IDBI Innovate 2026 · Challenge 1 (Wealth Advisory)**

Saarthi is an AI-powered digital wealth management prototype with an avatar-based
conversational interface, designed to sit inside IDBI Bank's mobile banking app.
It infers a customer's behavioural risk profile from spending/investment data
(via a trained ML model, not a one-time questionnaire), tracks goal-based
investing, generates proactive nudges, and answers questions through a
conversational avatar — with every recommendation traceable back to a reason.

This repo contains a working full-stack prototype:

- **`backend/`** — Python/FastAPI service: SQLite persistence, a synthetic
  dataset + trained scikit-learn risk-profiling model, rule-based
  recommendation/nudge engines, and an avatar chat endpoint (OpenAI via the
  OpenAI API, with an offline fallback responder).
- **`mobile/`** — React Native (Expo, TypeScript) app: Home, Goals, Talk
  (avatar chat) and Profile screens, matching the pitch-deck mockups.

**Full technical documentation** lives in [`docs/`](docs/):
- [`docs/SRS.md`](docs/SRS.md) — Software Requirements Specification.
- [`docs/FRONTEND.md`](docs/FRONTEND.md) — every screen/route, component, and the API client layer.
- [`docs/BACKEND.md`](docs/BACKEND.md) — full API reference table + a code walkthrough of every router/service/ML module.
- [`docs/SYSTEM_DESIGN.md`](docs/SYSTEM_DESIGN.md) — use-case diagram, DFDs, flowcharts, architecture/sequence diagrams, deployment view (Mermaid — renders on GitHub/VS Code).

---

## 1. Folder structure

```
saarthi-ai-wealth-avatar/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── .env.example              # copy to .env
│   ├── run.py                    # `python run.py` entrypoint
│   ├── saarthi.db                  # created on first run (sqlite)
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, startup/seed
│   │   ├── config.py             # env-driven settings (pydantic-settings)
│   │   ├── schemas.py            # Pydantic request/response models
│   │   ├── db/
│   │   │   ├── database.py       # SQLAlchemy engine/session
│   │   │   ├── models.py         # Customer, Goal, ChatMessage ORM models
│   │   │   └── seed.py           # seeds DB from the synthetic dataset
│   │   ├── ml/
│   │   │   ├── generate_dataset.py   # fabricates synthetic_customers.csv
│   │   │   ├── train_risk_model.py   # trains + saves the RandomForest model
│   │   │   ├── risk_model.py         # runtime inference wrapper
│   │   │   ├── data/                 # generated: synthetic_customers.csv
│   │   │   └── artifacts/            # generated: risk_model.joblib, metrics.json
│   │   ├── services/
│   │   │   ├── wealth_service.py         # Wealth Health Score
│   │   │   ├── goal_service.py           # goal funded % / on-track logic
│   │   │   ├── recommendation_service.py # asset allocation + goal top-up math
│   │   │   ├── nudge_service.py          # rule-based proactive nudges
│   │   │   └── avatar_service.py         # OpenAI call + offline fallback
│   │   └── routers/
│   │       ├── auth.py, users.py, goals.py
│   │       └── recommendations.py, nudges.py, chat.py
│   └── tests/
│       └── test_api.py           # pytest suite (12 tests, all passing)
└── mobile/
    ├── package.json, app.json, babel.config.js, tsconfig.json
    ├── .env.example              # copy to .env
    ├── App.tsx
    └── src/
        ├── api/client.ts         # typed fetch wrapper around the backend
        ├── types/index.ts        # shared TypeScript interfaces
        ├── theme/colors.ts       # IDBI brand palette (teal/orange)
        ├── context/SessionContext.tsx  # holds logged-in customer_id
        ├── navigation/RootNavigator.tsx # bottom tabs: Home/Goals/Talk/Profile
        ├── components/          # AvatarBubble, UserBubble, GoalCard, StatCard, NudgeCard
        └── screens/              # LoginScreen, HomeScreen, GoalsScreen, ChatScreen, ProfileScreen
```

---

## 2. How the pieces fit together

```
React Native app (Expo)  ──HTTP/JSON──▶  FastAPI backend  ──▶  SQLite (customers, goals, chats)
                                              │
                                              ├──▶ risk_model.joblib (scikit-learn RandomForest)
                                              │      trained on a synthetic 4,000-customer dataset
                                              │
                                              └──▶ avatar_service
                                                     ├─ if OPENAI_API_KEY set → OpenAI API
                                                     └─ else → rule-based templated responder
```

The ML model predicts a **risk_label** (conservative / moderate / aggressive)
from behavioural features (savings rate, SIP consistency, transaction
volatility, credit utilisation, goal horizon, etc.). Everything downstream —
asset allocation split and goal top-up sizing — is a **transparent formula**,
not a black box, so every number the app shows can be explained (this mirrors
the SEBI/RBI explainability expectations called out in the pitch deck).

---

## 3. Prerequisites

| Tool | Version used to build this | Check with |
|---|---|---|
| Python | 3.11+ (built/tested on 3.14) | `python --version` |
| Node.js | 20 LTS+ (built/tested on 24) | `node --version` |
| npm | 10+ | `npm --version` |
| Expo Go app | latest, on your phone (optional but easiest) | App Store / Play Store |

You do **not** need Docker, PostgreSQL, or any paid cloud account to run this
end-to-end — SQLite is used for storage and the avatar chat has a fully
offline fallback mode.

---

## 4. Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 4.1 Generate the synthetic dataset and train the ML model

The repo does not ship pre-trained model files — generate them locally
(takes well under a minute):

```bash
python -m app.ml.generate_dataset     # writes app/ml/data/synthetic_customers.csv
python -m app.ml.train_risk_model     # trains + writes app/ml/artifacts/risk_model.joblib
```

You should see an accuracy print around ~0.80–0.85 and a saved-model
confirmation. Both scripts are safe to re-run any time (they regenerate their
outputs from scratch with a fixed random seed, so results are reproducible).

### 4.2 Configure environment variables (API key)

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Open `.env`:

```ini
# Optional. Leave blank to use the offline fallback responder.
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=sqlite:///./saarthi.db
DEMO_CUSTOMER_ID=SAARTHI100000
SEED_CUSTOMER_COUNT=200
```

- **No API key?** Leave `OPENAI_API_KEY` blank. The `/chat` endpoint will
  use a rule-based responder that still answers using the customer's real
  profile/goals/risk data — the whole app runs end-to-end with **zero** paid
  services.
- **Want real LLM-generated avatar replies?** Get a key from
  https://platform.openai.com/api-keys, paste it into `.env` as
  `OPENAI_API_KEY=sk-...`, restart the server. If the key is invalid or
  a request fails for any reason, the backend automatically falls back to the
  offline responder rather than erroring out.

### 4.3 Run the server

```bash
python run.py
```

This starts uvicorn on `http://0.0.0.0:8000` with auto-reload. On first
request it creates `saarthi.db` and seeds it with 200 synthetic customers plus
3 demo goals for the demo customer.

Verify it's alive:

```bash
curl http://localhost:8000/health
# {"status":"ok","app":"Saarthi Wealth Avatar API"}
```

Interactive API docs (Swagger UI) are auto-generated at
`http://localhost:8000/docs`.

**Demo login:** `customer_id = SAARTHI100000` (the seeded demo customer with
3 pre-populated goals). Any of the other ~199 seeded `SAARTHI1000xx` IDs in
`app/ml/data/synthetic_customers.csv` also work for login, but only the demo
customer has goals pre-created.

### 4.4 Run the tests

```bash
pytest tests/ -v
```

12 tests covering auth, profile, wealth summary, risk profiling, goals CRUD,
recommendations, nudges, and chat (both the happy path and 404s). All pass
against a throwaway SQLite DB, so running the tests never touches your real
`saarthi.db`.

---

## 5. Mobile app (React Native / Expo) setup

```bash
cd mobile
npm install
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

### 5.1 Point the app at your backend

Open `mobile/.env`:

```ini
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

- **Running in a web browser or an Android/iOS emulator on the same
  machine as the backend:** `http://localhost:8000` works as-is (Android
  emulators actually need `http://10.0.2.2:8000` — Expo usually rewrites this
  for you, but if requests fail, switch to that explicitly).
- **Running on a physical phone via Expo Go:** `localhost` refers to the
  *phone*, not your computer. Find your computer's LAN IP
  (`ipconfig` on Windows / `ifconfig` or `ipconfig getifaddr en0` on
  macOS) and use e.g. `EXPO_PUBLIC_API_BASE_URL=http://192.168.1.23:8000`.
  Your phone and computer must be on the same Wi-Fi network, and Windows
  Firewall must allow inbound connections on port 8000 (accept the prompt
  the first time, or add a rule manually).

### 5.2 Start the app

Make sure the backend (`python run.py`) is already running, then:

```bash
npm start
```

This opens the Expo dev tools. From there:
- Press `a` for Android emulator, `i` for iOS simulator, `w` for web, or
- Scan the QR code with the **Expo Go** app on your phone (fastest path if
  you don't have emulators set up).

You should land on the **Saarthi** login screen pre-filled with the demo
customer ID (`SAARTHI100000`) — tap **Continue** to log in and see the Home,
Goals, Talk and Profile tabs populated with real data from the backend.

### 5.3 Type-check / lint

```bash
npx tsc --noEmit
```

This project type-checks cleanly with zero errors as-is.

---

## 6. Bank Staff Summary Dashboard

This is the deck's other half of the product: branch/RM staff get an
**aggregated sales-opportunity view** per customer — never the customer's raw
chat with Saarthi.

From the login screen, tap **"Sign in as bank staff instead"** and use the
seeded demo login `STAFF001` / `saarthi-demo`. This opens a separate stack (no
customer tabs) with:

- **Dashboard** — every seeded customer, sorted by top opportunity score, with
  an engagement badge (High/Medium/Low/No activity yet) derived from how many
  times they've messaged Saarthi.
- **Customer summary** — tap a row to see confidence-scored suitability for
  the four products the pitch deck calls out: **FD, Personal Loan, SIP/Mutual
  Fund, Insurance**, each 0–100% with a one-line rationale, plus an explicit
  banner: *"Raw chat transcript is private to the customer — staff see only
  these aggregated scores, never the conversation itself."*

How this is enforced, not just claimed:
- `backend/app/services/opportunity_service.py` computes every score from
  `Customer` fields and `ChatMessage` **counts/timestamps only** — it never
  reads `ChatMessage.content`.
- `backend/app/routers/staff.py` sits behind its own `BankStaff` login
  (`backend/app/security.py`, PBKDF2-hashed passwords) and a `get_current_staff`
  dependency — a customer's session token cannot call any `/staff/*` endpoint,
  and there is no endpoint anywhere that returns raw chat text to a staff
  caller (verified in `backend/tests/test_api.py::test_staff_summary_never_exposes_raw_chat_content`).

Scoring is intentionally rule-based and explainable (same philosophy as the
Wealth Health Score), not an ML black box — every percentage traces back to
concrete profile fields (idle cash, debt/equity mix, expense-to-income ratio,
card utilization, dependents, goal horizon, etc.).

---

## 7. What's real vs. what's simulated (be upfront about this)

- **Real:** the FastAPI backend, SQLite persistence, the scikit-learn risk
  model (genuinely trained, ~82-85% held-out accuracy on the synthetic
  dataset), the rule-based recommendation/nudge engines, and the full React
  Native UI — all of it runs and was tested end-to-end while building this.
- **Simulated (by necessity, for a hackathon prototype):** there is no real
  IDBI customer data, so a synthetic dataset stands in for it
  (`app/ml/generate_dataset.py` documents exactly how it's fabricated). Login
  is a mock lookup by `customer_id` with no password/OTP — a real deployment
  would sit behind IDBI's existing mobile-banking authentication. The avatar's
  voice/visual rendering (Polly/MetaHuman, per the pitch deck's architecture
  slide) isn't implemented here — the chat is text-based; wiring in real
  text-to-speech is future-development scope, not needed to validate the
  advisory logic itself.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| Mobile app shows "Could not reach the Saarthi backend" | Confirm `python run.py` is running and `EXPO_PUBLIC_API_BASE_URL` matches how your device reaches your computer (see 5.1). |
| `risk-profile` / `recommendations` return HTTP 503 | You haven't run the ML scripts yet — see step 4.1. |
| `ModuleNotFoundError` running Python scripts | Activate the virtualenv and re-run `pip install -r requirements.txt`. |
| Physical phone can't connect | Same Wi-Fi network as your computer + Windows Firewall allowing port 8000 + using LAN IP, not `localhost`. |
| `npm install` warnings about deprecated packages | Expected — these come from React Navigation/Expo's own transitive dependencies, not this project's code; safe to ignore for a prototype. |

---

## 9. Regenerating this from scratch

If you ever want a completely clean slate:

```bash
# backend
rm backend/saarthi.db backend/app/ml/data/synthetic_customers.csv backend/app/ml/artifacts/*
cd backend && python -m app.ml.generate_dataset && python -m app.ml.train_risk_model && python run.py

# mobile
rm -rf mobile/node_modules
cd mobile && npm install && npm start
```
