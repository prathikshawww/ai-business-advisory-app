import os
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import csv
import io
import db_config
from flask import Flask, request, jsonify
from flask_cors import CORS
import nlp_engine
import financial_calculator
import feasibility_module
import scheme_router

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get("query", "")

    intent, entities = nlp_engine.process_query(query)

    if intent in ("financial_profit", "compare_financials", "financial_revenue_growth"):
        response = scheme_router.handle_intent(intent, entities)
        result = {"message": response}
    else:
        result = {"message": "Sorry, I couldn't understand your request."}

    return jsonify(result)


@app.route("/api/financials")
def get_financials():
    conn = db_config.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT quarter, revenue, expenses FROM financials ORDER BY id;")
    rows = cur.fetchall()
    result = [
        {"quarter": row[0], "revenue": row[1], "expenses": row[2]}
        for row in rows
    ]
    cur.close()
    conn.close()
    return jsonify(result)


def generate_report():
    conn = db_config.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT quarter, revenue, expenses, revenue-expenses AS profit FROM financials;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Quarter", "Revenue", "Expenses", "Profit"])
    writer.writerows(rows)
    csv_data = output.getvalue()

    send_email_report(csv_data)


def send_email_report(csv_data):
    sender = os.getenv("REPORT_EMAIL_SENDER")
    recipient = os.getenv("REPORT_EMAIL_RECIPIENT")
    sender_password = os.getenv("REPORT_EMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["Subject"] = "Weekly Financial Report"
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText("Attached is the weekly financial report."))

    attachment = MIMEApplication(csv_data, Name="financial_report.csv")
    attachment["Content-Disposition"] = 'attachment; filename="financial_report.csv"'
    msg.attach(attachment)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, sender_password)
        server.send_message(msg)


scheduler = BackgroundScheduler()
scheduler.add_job(generate_report, "interval", weeks=1)
scheduler.start()


@app.route("/")
def home():
    return "Backend running with scheduled reports!"


if __name__ == "__main__":
    app.run(port=5000, debug=True)