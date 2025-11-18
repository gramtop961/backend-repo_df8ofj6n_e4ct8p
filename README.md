Przedszkole Miasteczkole — Aplikacja demonstracyjna

- Strona główna z opisem placówki i sekcjami informacyjnymi
- W prawym górnym rogu przycisk "Advent Calendar"
- Moduł Kalendarza Adwentowego: rejestracja rodzica (imię, e‑mail, telefon, imię dziecka) oraz zadania 1–24 grudnia
- Backend FastAPI zapisuje zgłoszenia i odpowiedzi w MongoDB
- Integracja z EmailJS (wymaga ustawienia kluczy w zmiennych środowiskowych)

Konfiguracja e‑mail (EmailJS)
- Service ID: miasteczkole
- Public key: JObp6Q5RF3YHKjdHI
- Private key: THI4AB3xM5NMU-UZFSjX7

Ustaw w backend/.env (jeśli chcesz włączyć wysyłkę):
EMAILJS_SERVICE_ID=miasteczkole
EMAILJS_PUBLIC_KEY=JObp6Q5RF3YHKjdHI
EMAILJS_PRIVATE_KEY=THI4AB3xM5NMU-UZFSjX7
EMAILJS_TEMPLATE_REG=advent_registration
SCHOOL_EMAIL=powiadomienia@twojadomena.pl
FROM_EMAIL=no-reply@twojadomena.pl

Szablon e‑mail (template advent_registration):
Temat: {{subject}}
Treść (HTML):
<p>Dzień dobry {{to_name}},</p>
<p>Dziękujemy za zgłoszenie do Kalendarza Adwentowego w {{school_name}}.</p>
{{#if child_name}}<p>Imię dziecka: <strong>{{child_name}}</strong></p>{{/if}}
<p>Życzymy miłej zabawy!</p>
<p>Pozdrawiamy,<br/>Zespół {{school_name}}</p>
