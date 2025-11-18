import os
from datetime import datetime, date
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests

from database import create_document, get_documents, db
from schemas import AdventRegistration, AdventSubmission, School

app = FastAPI(title="Przedszkole Miasteczkole API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Config from environment ----
EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID", "miasteczkole")
EMAILJS_TEMPLATE_REG = os.getenv("EMAILJS_TEMPLATE_REG", "advent_registration")
EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY", "")
EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@miasteczkole.pl")
SCHOOL_EMAIL = os.getenv("SCHOOL_EMAIL", "info@miasteczkole.pl")
SCHOOL_NAME = os.getenv("SCHOOL_NAME", "Przedszkole Miasteczkole")


# ---- Static school info (returned by API) ----
SCHOOL_INFO = School(
    name="Przedszkole Miasteczkole",
    description=(
        "Przedszkole prowadzi zajęcia dla dzieci od 3 do 6 lat. Stawia na rozwój "
        "społeczny, emocjonalny i ruchowy. Zapewnia bezpieczne warunki i stałą opiekę kadry."
    ),
    mission="Zapewnić dziecku dobre warunki rozwoju. Wspierać ciekawość. Uczyć przez działanie.",
    email=SCHOOL_EMAIL,
    opening_hours="7:00 - 17:00",
)

# Advent tasks content (simple demo content for 1..24)
ADVENT_TASKS: Dict[int, str] = {
    1: "Narysuj swoją ulubioną zimową zabawę.",
    2: "Policz ile choinek widzisz na obrazku.",
    3: "Zaśpiewaj fragment ulubionej kolędy.",
    4: "Ułóż 3 zielone klocki i 1 czerwony – policz razem.",
    5: "Zrób 5 podskoków jak renifer.",
    6: "Narysuj prezent dla przyjaciela.",
    7: "Wymień 3 zimowe ubrania.",
    8: "Ułóż serduszko z klocków.",
    9: "Policz do 10 razem z rodzicem.",
    10: "Zatańcz śnieżynkowy taniec przez 10 sekund.",
    11: "Namaluj śnieżynkę palcami.",
    12: "Powiedz rymowankę o Mikołaju.",
    13: "Zbuduj choinkę z klocków.",
    14: "Nazwij 4 kolory bombek.",
    15: "Zrób 3 głębokie wdechy i wydechy.",
    16: "Narysuj pierniczka.",
    17: "Posłuchaj krótkiej melodii i powtórz rytm.",
    18: "Wymień 3 zimowe sporty.",
    19: "Ułóż obrazek z 4 elementów.",
    20: "Napisz swoje imię (z pomocą rodzica).",
    21: "Policz 7 gwiazdek na obrazku.",
    22: "Zrób laurkę dla rodziców.",
    23: "Zaśpiewaj kolędę z rodziną.",
    24: "Złóż życzenia świąteczne – Wesołych Świąt!",
}


@app.get("/")
def read_root():
    return {"message": "API Przedszkola Miasteczkole działa"}


@app.get("/api/school/info")
def get_school_info():
    # Add more detailed info for sections
    return {
        "nazwa": "Przedszkole Miasteczkole",
        "opis": SCHOOL_INFO.description,
        "misja": SCHOOL_INFO.mission,
        "oferta": [
            "Zajęcia edukacyjne zgodne z podstawą programową.",
            "Zabawy ruchowe.",
            "Nauka poprzez gry.",
            "Zajęcia plastyczne.",
            "Zajęcia muzyczne.",
            "Zajęcia językowe.",
            "Wyjścia na świeże powietrze.",
        ],
        "dodatkowe": [
            "Rytmika.",
            "Zajęcia sportowe.",
            "Zajęcia sensoryczne.",
            "Podstawy języka angielskiego.",
        ],
        "opieka": [
            "Stała opieka nauczycieli.",
            "Monitorowany budynek.",
            "Zabezpieczony teren.",
            "Zdrowe posiłki.",
            "Odpowiednie warunki sanitarne.",
        ],
        "grupy": [
            "Grupa młodsza 3-4 lata.",
            "Grupa średnia 4-5 lat.",
            "Grupa starsza 5-6 lat.",
        ],
        "kadra": [
            "Nauczyciele z kwalifikacjami.",
            "Pomoc nauczyciela.",
            "Logopeda wspierający rozwój mowy.",
            "Psycholog dostępny dla rodziców.",
        ],
        "dzien": [
            "Powitanie i swobodna zabawa.",
            "Zajęcia edukacyjne.",
            "Drugie śniadanie.",
            "Zabawy ruchowe.",
            "Obiad.",
            "Odpoczynek.",
            "Zajęcia popołudniowe.",
            "Odbiór dzieci.",
        ],
        "posilki": [
            "Świeże i zbilansowane.",
            "Śniadanie, obiad, podwieczorek.",
            "Menu dostosowane do alergii.",
        ],
        "rekrutacja": [
            "Nabór całoroczny.",
            "Przyjęcia według kolejności zgłoszeń.",
            "Wymagane dokumenty: karta zgłoszenia, zgoda rodziców.",
        ],
        "kontakt": {
            "email": SCHOOL_EMAIL,
            "telefon": None,
            "adres": None,
            "godziny": "7:00 - 17:00",
        },
    }


class RegisterResponse(BaseModel):
    status: str
    message: str


def send_emailjs(template_id: str, params: Dict[str, Any]) -> bool:
    """Send email via EmailJS REST API."""
    if not EMAILJS_PRIVATE_KEY:
        return False
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": template_id,
        "user_id": EMAILJS_PUBLIC_KEY,
        "accessToken": EMAILJS_PRIVATE_KEY,
        "template_params": params,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code in (200, 202)
    except Exception:
        return False


@app.post("/api/advent/register", response_model=RegisterResponse)
def advent_register(reg: AdventRegistration):
    # Save registration
    reg_id = create_document("adventregistration", reg)

    # Notify parent
    subject = f"{SCHOOL_NAME} – Potwierdzenie zgłoszenia do Kalendarza Adwentowego"
    params_parent = {
        "to_email": reg.email,
        "to_name": reg.parent_name,
        "child_name": reg.child_name,
        "subject": subject,
        "school_name": SCHOOL_NAME,
    }
    sent_parent = send_emailjs(EMAILJS_TEMPLATE_REG, params_parent)

    # Notify school
    params_school = {
        "to_email": SCHOOL_EMAIL,
        "to_name": "Sekretariat",
        "parent_name": reg.parent_name,
        "child_name": reg.child_name,
        "phone": reg.phone,
        "email": reg.email,
        "subject": f"Nowa rejestracja – {reg.child_name}",
        "school_name": SCHOOL_NAME,
    }
    sent_school = send_emailjs(EMAILJS_TEMPLATE_REG, params_school)

    msg = "Zapisano zgłoszenie. "
    if not (sent_parent and sent_school):
        msg += "Wiadomość e-mail nie została wysłana automatycznie. Skonfiguruj EmailJS (template: advent_registration)."
    else:
        msg += "Wysłano potwierdzenie e-mail."

    return {"status": "ok", "message": msg}


@app.get("/api/advent/days")
def get_advent_days():
    today = date.today()
    unlocked = 24 if (today.month == 12 and today.day >= 24) else (today.day if today.month == 12 else 0)
    days: List[Dict[str, Any]] = []
    for d in range(1, 24 + 1):
        days.append({
            "day": d,
            "available": d <= unlocked,
            "task": ADVENT_TASKS.get(d, "Zadanie niespodzianka"),
        })
    return {"days": days, "unlocked": unlocked}


@app.post("/api/advent/submit")
def submit_advent(sub: AdventSubmission):
    # Save submission (answer optional)
    create_document("adventsubmission", sub)
    return {"status": "ok", "message": "Dziękujemy! Zapisano odpowiedź."}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["emailjs_configured"] = bool(EMAILJS_PRIVATE_KEY and EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID)
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
