from sqlalchemy import or_

from app.models import Medicine


def answer_chatbot(message):
    text = (message or "").strip().lower()
    if not text:
        return {"answer": "Ask me about a medicine, alternatives, prescription text, or stock.", "matches": []}

    meds = Medicine.query.filter(
        or_(
            Medicine.name.ilike(f"%{text}%"),
            Medicine.category.ilike(f"%{text}%"),
            Medicine.description.ilike(f"%{text}%"),
        )
    ).limit(8).all()

    if "alternative" in text or "substitute" in text:
        token = text.replace("alternative", "").replace("substitute", "").strip()
        base = Medicine.query.filter(Medicine.name.ilike(f"%{token}%")).first()
        if base:
            meds = Medicine.query.filter(Medicine.category == base.category, Medicine.id != base.id).limit(8).all()
            return {
                "answer": f"Possible alternatives in {base.category}. Verify strength, formulation, and prescription before dispensing.",
                "matches": [_med(m) for m in meds],
            }

    if "stock" in text or "reorder" in text:
        meds = Medicine.query.filter(Medicine.stock <= Medicine.min_stock).order_by(Medicine.stock.asc()).limit(8).all()
        return {"answer": "These medicines need stock attention.", "matches": [_med(m) for m in meds]}

    if "prescription" in text or "rx" in text:
        return {
            "answer": "I can summarize prescription text, flag expired prescriptions, and highlight medicines that require pharmacist verification.",
            "matches": [_med(m) for m in meds],
        }

    return {
        "answer": "I found matching medicines. Confirm dosage and prescription rules before sale.",
        "matches": [_med(m) for m in meds],
    }


def _med(medicine):
    return {
        "id": medicine.id,
        "name": medicine.name,
        "category": medicine.category,
        "stock": medicine.stock,
        "mrp": float(medicine.mrp),
        "rx_required": medicine.rx_required,
    }
