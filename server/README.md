# Optional teacher-managed student accounts

This server is separate from static hosting. GitHub Pages cannot run it. The public PWA shows a clear not-configured message when no account API exists; it never pretends that browser-only profiles are authenticated accounts.

## Local setup

Use Python 3.11+ with SQLite and hashlib.scrypt support. No third-party packages required.

```
python3 server/server.py --create-teacher
python3 server/server.py
```

The first command interactively asks for a teacher ID, display label and password. Do not place real passwords on the command line, in source or in GitHub. Open http://127.0.0.1:4174 and use Student sign-in. A signed-in teacher can create students, view aggregate school-milestone progress and reset a student's password. Students can log in, save progress and load it on another device.

Use student aliases/IDs rather than real names, email addresses or phone numbers. Share initial passwords privately with the student or guardian. The database and session cookies must never be included in the public repository or downloadable source.

## Remote hosting prerequisites

Choose a persistent server/VPS accessible from the students' networks, with Python, a persistent data volume, an HTTPS reverse proxy, regular encrypted backups and a domain. Set:

- `APP_ORIGIN=https://your-actual-domain` exactly, without a trailing slash.
- `FOOTPATH_DATA=/persistent/private/footpath-data` outside the web directory.

Run the Python service on loopback behind your reverse proxy; terminate TLS there. The default loopback binding intentionally does not expose the development service. Do not expose the account server directly over HTTP. The service uses scrypt password hashes with individual salts, opaque hashed sessions, HttpOnly/SameSite cookies, Secure cookies under HTTPS, exact-origin mutation checks, teacher ownership checks, revision conflict checking and login rate limiting. Rate limiting is in memory for a single-process deployment; enforce a request limit at the reverse proxy too. A deployment owner must review backups, retention and operational recovery before enrolling real pupils. No email password recovery is provided; teachers reset their own students' passwords.

No server or domain has been purchased or configured. Mainland reachability has not been tested; do not claim access from all Chinese networks. Static guest learning is available separately. Hosting in mainland China may require provider-specific domain/registration steps; confirm these with the chosen provider.

The server stores client-submitted learning progress, not tamper-resistant examination results. The teaching app is not a secure proctored assessment platform. Native app-store packaging is separate.
