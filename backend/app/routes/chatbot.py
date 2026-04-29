from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.ai import answer_chatbot
from app.utils.security import validate_json
from marshmallow import Schema, fields

bp = Blueprint("chatbot", __name__, url_prefix="/api/ai")


class ChatSchema(Schema):
    message = fields.Str(required=True)
    history = fields.List(fields.Dict(), load_default=[])


@bp.post("/chat")
@jwt_required()
def chat():
    data = validate_json(ChatSchema())
    result = answer_chatbot(data["message"], history=data.get("history", []))
    return jsonify(result)
