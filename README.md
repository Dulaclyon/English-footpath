# Little by Little — English Footpath

Original responsive English-learning PWA for iPhone, Android, tablets and desktop. School progression runs from Grade 3 to senior high, with an introductory Academic IELTS 7.0+ preparation bridge. This is a working prototype and starter course, not a complete curriculum or an IELTS band predictor.

## Included

- Ten school milestones and thirty original short readings, with three application questions per reading.
- Grammar maps with Chinese explanations; forty categorised vocabulary items and twenty useful expressions with meaning contrasts, collocations and examples.
- 50 scored retrieval attempts per school milestone, optionally 60. Balanced category minimums: 15 grammar, 15 vocabulary, 10 expression and 10 reading attempts. Complete all three reading checks and score 8/10 on a separate mastery check to advance.
- Six Grade 7 microsteps informed by the supplied sample-question types. Each has its own 50/60-attempt and 8/10 advancement gate.
- Four introductory IELTS skill steps: reading, listening, writing and speaking. Each has a practice gate; writing/speaking performance still needs teacher assessment. Audio is device-generated, not authentic test audio.
- Teaching mode: 75–200% lesson zoom, focus layout, browser full screen where supported, pen, highlighter, eraser, Undo and movable text notes. Ink is a temporary screen overlay and clears when lesson/zoom/layout changes.
- Offline lesson caching after the first successful online visit; local progress and JSON backup import/export.
- Optional Python/SQLite student-account server: teachers create student IDs, reset passwords and view aggregate progress; students save/load their progress. **This server is not running on GitHub Pages.**

## Run guest app

```
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173. There is no build step or frontend dependency. HTTPS is required for web-app installation outside localhost. Fonts are local system fallbacks; no Google Fonts request is required. Audio voices vary by device.

## Run teacher/student accounts

Read [server/README.md](server/README.md). Create a teacher interactively and serve the app with the included Python server. Remote use needs an HTTPS host, persistent storage and operational setup. Static hosting deliberately reports that accounts are not configured; it does not present local profiles as authenticated accounts.

## Install on phones

- iPhone/iPad: Safari → Share → Add to Home Screen.
- Android: Chrome → menu → Install app or Add to Home screen, where offered.

Browser installation was not verified on physical devices. Mainland China reachability is unverified; test from students' actual networks before classroom use. No domain or account host has been purchased. There is no App Store or Google Play release.

## Verification

```
node tests/learning.test.cjs
python3 tests/accounts_test.py
python3 scripts/package.py
```

The account test runs a temporary local server and database; it does not register real students. See [qa/ralph-loop.md](qa/ralph-loop.md) for the three-cycle test record. The learning tests run in a lightweight DOM harness; browser checks separately verify user-facing layout and interactions.

## Distribution

The public repository was created from scratch at https://github.com/Dulaclyon/English-footpath. A GitHub Pages Actions workflow deploys `dist/`. Configure Settings → Pages → Source: GitHub Actions. The app's source-download button downloads `dist/english-footpath-source.zip`, including the optional account server and setup documentation, but no database, session data or credentials.

## Content and research

Read [CURRICULUM.md](CURRICULUM.md) and the [Grade 7 screenshot/question analysis](dist/grade7-analysis.html). The public repository contains no supplied examination photographs or student identifiers. Grade allocation is an editorial scaffold informed by national standards, not a claim of one mandatory sequence for all textbooks. Sample texts and app questions are original.

The 50/60 count is a requested product rule, not a universal scientific mastery threshold. The current banks are small and intentionally repeat; lasting learning needs varied contexts and delayed recall. Client-side progress is not a secure examination record. Previously mastered lessons stay unlocked if the practice target is later raised.
