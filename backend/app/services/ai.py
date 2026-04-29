import os
from sqlalchemy import or_
from app.models import Medicine

# ── Groq client (lazy-initialised so the app still boots without the key) ──────
_groq_client = None

def _get_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            try:
                from groq import Groq
                _groq_client = Groq(api_key=api_key)
            except Exception:
                pass
    return _groq_client


SYSTEM_PROMPT = """You are MedBot, an expert AI pharmacy assistant built into MedStore — a pharmacy management SaaS.

Your role is to help pharmacists and pharmacy staff with:
- Medicine information (dosage, side effects, drug interactions, contraindications)
- Inventory and stock management advice
- Prescription interpretation and verification tips
- Generic alternatives and substitutes
- GST and billing guidance for Indian pharmacies
- Regulatory compliance (Schedule H, Schedule H1, Schedule X drugs)
- Expiry management and storage guidance
- Patient counselling tips

Rules:
1. Always recommend consulting a licensed doctor or senior pharmacist for clinical decisions.
2. Never provide dosage advice that overrides a doctor's prescription.
3. Be concise but comprehensive. Use bullet points when listing multiple items.
4. When the user asks about a specific medicine from the database, the system will inject live stock data — reference it directly.
5. Respond in a professional, warm, and helpful tone suitable for pharmacy staff.
6. For Indian pharmacy context: use INR (Rs), reference CDSCO regulations, mention generic names alongside brand names.
"""


def _build_medicine_context(message: str) -> str:
    """Query the DB for relevant medicines and return a formatted context string."""
    text = (message or "").strip()
    if not text:
        return ""

    # Search medicines matching the query
    meds = Medicine.query.filter(
        or_(
            Medicine.name.ilike(f"%{text}%"),
            Medicine.category.ilike(f"%{text}%"),
            Medicine.manufacturer.ilike(f"%{text}%"),
            Medicine.description.ilike(f"%{text}%"),
        )
    ).limit(10).all()

    # Also check low-stock if user asks about stock/reorder
    low_stock_meds = []
    lower = text.lower()
    if any(kw in lower for kw in ["stock", "reorder", "low", "shortage", "inventory"]):
        low_stock_meds = Medicine.query.filter(
            Medicine.stock <= Medicine.min_stock
        ).order_by(Medicine.stock.asc()).limit(8).all()

    context_parts = []

    if meds:
        lines = ["**Matching medicines in your inventory:**"]
        for m in meds:
            status = "⚠️ LOW STOCK" if m.stock <= m.min_stock else "✅ In Stock"
            lines.append(
                f"- {m.name} | Category: {m.category} | Stock: {m.stock} units | "
                f"MRP: Rs {m.mrp:.2f} | Expiry: {m.expiry_date} | "
                f"{'Rx Required' if m.rx_required else 'OTC'} | {status}"
            )
        context_parts.append("\n".join(lines))

    if low_stock_meds:
        lines = ["**Medicines needing restock:**"]
        for m in low_stock_meds:
            lines.append(
                f"- {m.name}: {m.stock}/{m.min_stock} units (min stock: {m.min_stock})"
            )
        context_parts.append("\n".join(lines))

    return "\n\n".join(context_parts)


def answer_chatbot(message: str, history: list = None) -> dict:
    """
    Main chatbot handler. Uses Groq LLM with pharmacy system prompt and live DB context.
    Falls back to rule-based responses if Groq is unavailable.
    """
    text = (message or "").strip()
    if not text:
        return {
            "answer": "Hello! I'm MedBot 🤖 — your pharmacy AI assistant. Ask me about medicines, stock, prescriptions, or billing.",
            "matches": [],
            "source": "local"
        }

    # Build live DB context
    db_context = _build_medicine_context(text)

    client = _get_client()

    if client:
        try:
            # Build message array for the LLM
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Inject DB context as a system message if we have relevant data
            if db_context:
                messages.append({
                    "role": "system",
                    "content": f"Live inventory data from the database:\n\n{db_context}"
                })

            # Add conversation history (last 10 turns max)
            if history:
                for turn in history[-10:]:
                    if turn.get("role") in ("user", "assistant") and turn.get("content"):
                        messages.append({"role": turn["role"], "content": turn["content"]})

            # Add current user message
            messages.append({"role": "user", "content": text})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.6,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content.strip()

            # Also return matching medicine objects for the frontend cards
            matches = _get_matches(text)
            return {"answer": answer, "matches": matches, "source": "groq"}

        except Exception as e:
            # Fallback if Groq call fails
            return _rule_based(text, error=str(e))

    # No Groq client — rule-based fallback
    return _rule_based(text)


def _get_matches(text: str) -> list:
    """Return serialised medicine matches for the frontend to display as cards."""
    lower = text.lower()
    if any(kw in lower for kw in ["stock", "reorder", "low", "shortage"]):
        meds = Medicine.query.filter(
            Medicine.stock <= Medicine.min_stock
        ).order_by(Medicine.stock.asc()).limit(6).all()
    else:
        meds = Medicine.query.filter(
            or_(
                Medicine.name.ilike(f"%{text}%"),
                Medicine.category.ilike(f"%{text}%"),
            )
        ).limit(6).all()
    return [_med(m) for m in meds]


def _rule_based(text: str, error: str = None) -> dict:
    """Simple keyword-based fallback used when Groq is unavailable."""
    lower = text.lower()

    if any(kw in lower for kw in ["stock", "reorder", "low", "inventory"]):
        meds = Medicine.query.filter(
            Medicine.stock <= Medicine.min_stock
        ).order_by(Medicine.stock.asc()).limit(8).all()
        return {
            "answer": "These medicines are at or below minimum stock levels and need reordering.",
            "matches": [_med(m) for m in meds],
            "source": "local"
        }

    if any(kw in lower for kw in ["alternative", "substitute", "generic"]):
        # Try to find a medicine name in the query
        words = [w for w in lower.split() if len(w) > 4]
        for word in words:
            base = Medicine.query.filter(Medicine.name.ilike(f"%{word}%")).first()
            if base:
                alts = Medicine.query.filter(
                    Medicine.category == base.category,
                    Medicine.id != base.id
                ).limit(8).all()
                return {
                    "answer": f"Possible alternatives in the {base.category} category. Always verify strength and formulation.",
                    "matches": [_med(m) for m in alts],
                    "source": "local"
                }

    if "prescription" in lower or "rx" in lower or "schedule" in lower:
        return {
            "answer": (
                "**Prescription medicines (Rx):**\n"
                "- Schedule H drugs require a valid prescription from a registered medical practitioner.\n"
                "- Schedule H1 drugs (like antibiotics) need prescription retention for 2 years.\n"
                "- Always verify the doctor's registration number before dispensing.\n"
                "- Never dispense Schedule X (narcotic/psychotropic) without special license."
            ),
            "matches": [],
            "source": "local"
        }

    # Generic medicine search
    meds = Medicine.query.filter(
        or_(
            Medicine.name.ilike(f"%{text}%"),
            Medicine.category.ilike(f"%{text}%"),
        )
    ).limit(6).all()

    fallback_note = f" (Note: AI unavailable — {error})" if error else ""
    return {
        "answer": f"Here are matching medicines from your inventory.{fallback_note} Confirm dosage and prescription rules before dispensing.",
        "matches": [_med(m) for m in meds],
        "source": "local"
    }


def _med(medicine) -> dict:
    return {
        "id": medicine.id,
        "name": medicine.name,
        "category": medicine.category,
        "stock": medicine.stock,
        "min_stock": medicine.min_stock,
        "mrp": float(medicine.mrp),
        "rx_required": medicine.rx_required,
        "expiry_date": str(medicine.expiry_date),
        "status": "low_stock" if medicine.stock <= medicine.min_stock else "ok",
    }
