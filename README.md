# Little by Little — English Footpath
Original, framework-free responsive PWA for Grades 3–12. Ten representative grammar milestones, thirty original short readings, Chinese explanations, knowledge maps, retrieval practice, mastery checks, local progress backups and offline caching. This is a starter course, not a complete national curriculum or a proficiency test.

## Run
Serve `dist/` with any static HTTP server, for example `python3 -m http.server 4173 --directory dist`. Open localhost:4173. HTTPS is required for installation and service workers outside localhost. No API keys, build tools or dependencies required. System audio voices vary by device.

## Learning rules
Sequential unlock: all three reading comprehension checks + chosen 50/60 scored practice attempts + 8/10 mastery score. Missed questions are prioritised. Correct practice schedules a review after one day, mistakes after ten minutes. Small question bank repeats intentionally; production expansion should include substantially more varied retrieval, longer texts, delayed mastery verification and teacher review. Completion and accuracy are distinct. Previously mastered lessons stay mastered if target is raised.

## Devices
Responsive for iPhone, Android, tablets and desktop. Install via Safari Share > Add to Home Screen or Chrome Install app. Lessons cache after first successful online visit. Progress is localStorage, not cloud synced; use JSON export/import. Do not treat this local client-side learning gate as a secure assessment system.

## Hosting
Deploy contents of dist to any HTTPS static host. A GitHub Pages Actions workflow is included. Configure repository Settings > Pages > Source: GitHub Actions. On GitHub Pages the URL will include the repository name; all asset paths are relative.

## Research
Consulted 2026-10-27:
- https://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html
- https://www.ictr.edu.cn/download_center/ywjy/p/1.html
- https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517522153664167.pdf
The compulsory standard provides attainment bands, not a single mandatory grade-by-grade grammar sequence. This implementation's grade allocation is editorial. Content is original; no textbook passages were copied. The 50/60 target is a product preference, not a universal evidence-based mastery threshold.

## Store publication
This PWA is not an App Store or Google Play listing. Native packaging (for example with Capacitor), physical-device QA, developer accounts, signing, accessibility/privacy review and store submission are separate release tasks. No child accounts, advertising, analytics or server collection are implemented. Google Fonts is an optional external font request; device fonts work offline.
