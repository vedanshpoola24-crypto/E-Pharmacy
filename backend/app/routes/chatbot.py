from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.schemas import ChatSchema
from app.services.ai import answer_chatbot
from app.utils.security import validate_json

bp = Blueprint("chatbot", __name__, url_prefix="/api/ai")


@bp.post("/chat")
@jwt_required()
def chat():
    data = validate_json(ChatSchema())
    return jsonify(answer_chatbot(data["message"]))
