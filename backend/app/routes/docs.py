from flask import Blueprint, jsonify

bp = Blueprint("docs", __name__)


OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "MedStore SaaS API", "version": "1.0.0"},
    "servers": [{"url": "/api"}],
    "components": {
        "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
    },
    "security": [{"bearerAuth": []}],
    "paths": {
        "/health": {"get": {"summary": "Health check", "responses": {"200": {"description": "OK"}}}},
        "/auth/register": {"post": {"summary": "Register user"}},
        "/auth/login": {"post": {"summary": "Login and return JWT"}},
        "/medicines": {"get": {"summary": "List medicines"}, "post": {"summary": "Create medicine"}},
        "/medicines/{id}": {"put": {"summary": "Update medicine"}, "delete": {"summary": "Delete medicine"}},
        "/suppliers": {"get": {"summary": "List suppliers"}, "post": {"summary": "Create supplier"}},
        "/bills": {"get": {"summary": "List bills"}, "post": {"summary": "Create GST invoice"}},
        "/bills/{id}/refund": {"post": {"summary": "Refund bill and restore stock"}},
        "/prescriptions": {"get": {"summary": "List prescriptions"}, "post": {"summary": "Upload prescription"}},
        "/dashboard": {"get": {"summary": "Dashboard analytics"}},
        "/reports/analytics": {"get": {"summary": "Sales, GST, inventory, profit reports"}},
        "/notifications": {"get": {"summary": "List notifications"}},
        "/ai/chat": {"post": {"summary": "AI medicine assistant"}},
    },
}


@bp.get("/openapi.json")
def openapi():
    return jsonify(OPENAPI)


@bp.get("/api/docs")
def swagger_ui():
    return """
<!doctype html>
<html><head><title>MedStore API Docs</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"></head>
<body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'});</script></body></html>
"""
