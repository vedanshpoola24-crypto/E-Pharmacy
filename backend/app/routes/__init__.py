from app.routes import auth, bills, chatbot, customers, dashboard, docs, health, medicines, notifications, prescriptions, suppliers


def register_blueprints(app):
    for module in [health, auth, customers, suppliers, medicines, bills, prescriptions, dashboard, notifications, chatbot, docs]:
        app.register_blueprint(module.bp)
