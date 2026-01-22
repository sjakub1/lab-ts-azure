from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Transaction
import os
from dotenv import load_dotenv

import csv
import io
from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

load_dotenv()

app = Flask(__name__)

# Needed for flash messages
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# DB config
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DB")
port = os.getenv("MYSQL_PORT", "3306")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def _get_blob_service_client() -> BlobServiceClient:
    """
    Prefers Managed Identity (DefaultAzureCredential) when AZURE_STORAGE_ACCOUNT_NAME is set.
    Falls back to connection string if AZURE_STORAGE_CONNECTION_STRING is set.
    """
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)

    if not account_name:
        raise RuntimeError(
            "Missing storage configuration. Set AZURE_STORAGE_ACCOUNT_NAME "
            "(for Managed Identity) or AZURE_STORAGE_CONNECTION_STRING."
        )

    credential = DefaultAzureCredential()
    account_url = f"https://{account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=credential)


def _sanitize_filename(name: str) -> str:
    # Very small sanitization: keep simple chars and enforce .csv
    name = (name or "").strip()
    if not name:
        name = "transactions"

    safe = []
    for ch in name:
        if ch.isalnum() or ch in ("-", "_"):
            safe.append(ch)
        elif ch in (" ", "."):
            safe.append("-")
    filename = "".join(safe).strip("-")
    if not filename.lower().endswith(".csv"):
        filename += ".csv"
    return filename


@app.route("/")
def index():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense
    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        t_type = request.form["type"]
        description = request.form["description"]
        amount = float(request.form["amount"])
        new_t = Transaction(type=t_type, description=description, amount=amount)
        db.session.add(new_t)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/export", methods=["POST"])
def export():
    # 1) Read filename from form
    filename_input = request.form.get("filename", "")
    filename = _sanitize_filename(filename_input)

    # 2) Build CSV in-memory
    transactions = Transaction.query.order_by(Transaction.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "description", "amount"])

    for t in transactions:
        writer.writerow([t.id, t.type, t.description, f"{t.amount:.2f}"])

    csv_text = output.getvalue()
    csv_bytes = csv_text.encode("utf-8")

    # 3) Upload to Blob Storage
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "exports")
    prefix = os.getenv("AZURE_STORAGE_BLOB_PREFIX", "").strip("/")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    blob_name = f"{filename.rsplit('.', 1)[0]}-{timestamp}.csv"
    if prefix:
        blob_name = f"{prefix}/{blob_name}"

    try:
        bsc = _get_blob_service_client()
        container_client = bsc.get_container_client(container_name)

        # Create container if it doesn't exist (nice for labs)
        try:
            container_client.create_container()
        except Exception:
            pass

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            csv_bytes,
            overwrite=True,
            content_settings=ContentSettings(
                content_type="text/csv; charset=utf-8"
            ),
        )

        flash(f"Export uploaded to Blob Storage as: {blob_name}", "success")
    except Exception as e:
        flash(f"Export failed: {e}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)