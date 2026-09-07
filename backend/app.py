import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config import get_connection
from flask import Flask, request, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from database.models import db, User
from dotenv import load_dotenv
from nlp_engine import process_query
from financial_calculator import calculate
from scheme_router import find_scheme


load_dotenv()

app = Flask(__name__)
CORS(app)

# Environment variables (make sure you set these in a .env file)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
SECRET_KEY = os.getenv("SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Serializer for secure tokens
serializer = URLSafeTimedSerializer(SECRET_KEY)


# Function to send reset email
def send_reset_email(to_email, token):
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    html_content = f"""
    <html>
      <body>
        <p>Click here to reset your password:</p>
        <a href="{reset_link}">{reset_link}</a>
      </body>
    </html>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="Password Reset Request",
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print("Error sending email:", str(e))
        return False


# Route 1: Request reset
@app.route("/api/request-reset", methods=["POST"])
def request_reset():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    token = serializer.dumps(email, salt="password-reset-salt")
    print("DEBUG - Reset token:", token)
    success = send_reset_email(email, token)

    # Always return the same message, whether or not the email exists,
    # so attackers can't use this endpoint to check which emails are registered
    return jsonify({"message": "If that email exists, a reset link has been sent"}), 200


# Route 2: Reset password
@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    try:
        # Verify token (valid for 1 hour)
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
def get_financial_comparison():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT quarter, revenue, expenses FROM financials ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return "No financial data available yet."

    quarter, revenue, expenses = row
    profit = revenue - expenses
    margin = round((profit / revenue) * 100, 2) if revenue else 0

    return (f"In {quarter}: Revenue ₹{revenue}, Expenses ₹{expenses}, "
            f"Profit ₹{profit} ({margin}% margin).")


def get_revenue_growth():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT quarter, revenue FROM financials ORDER BY id DESC LIMIT 2;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if len(rows) < 2:
        return "Not enough data yet to calculate growth."

    (latest_quarter, latest_revenue), (prev_quarter, prev_revenue) = rows

    if not prev_revenue:
        return f"Revenue for {latest_quarter} is ₹{latest_revenue}, but no prior quarter to compare against."

    growth = round(((latest_revenue - prev_revenue) / prev_revenue) * 100, 2)
    return (f"Revenue grew {growth}% from {prev_quarter} (₹{prev_revenue}) "
            f"to {latest_quarter} (₹{latest_revenue}).")
@app.route("/api/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"message": "Please enter a question."}), 400

    intent, entities_list = process_query(question)
    entities = {label: text for text, label in entities_list}

    if intent == "financial_profit":
       result = calculate(entities, question)
       message = result["calculation"]
    elif intent == "compare_financials":
        message = get_financial_comparison()
    elif intent == "financial_revenue_growth":
        message = get_revenue_growth()
    else:
        scheme_result = find_scheme(entities)
        message = scheme_result["scheme"]

    return jsonify({"message": message}), 200


if __name__ == "__main__":
    app.run(debug=False)