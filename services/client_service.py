"""Client and brand profile application services."""
from database.connection import get_connection

CLIENT_FIELDS = [
 "company_name","industry","category","website_url","website_status","location",
 "company_description","products_services","pricing","usp","target_audience",
 "ideal_customer_profile","pain_points","competitors","objectives","monthly_budget",
 "preferred_language","brand_voice","brand_guidelines","prohibited_topics","contact_details"
]

def list_clients(search=""):
    with get_connection() as c:
        if search.strip():
            q = f"%{search.strip()}%"
            rows = c.execute("""SELECT id, company_name, industry, location, website_url, objectives, updated_at
                FROM clients WHERE company_name LIKE ? OR industry LIKE ? OR location LIKE ?
                ORDER BY company_name""", (q,q,q)).fetchall()
        else:
            rows = c.execute("""SELECT id, company_name, industry, location, website_url, objectives, updated_at
                FROM clients ORDER BY company_name""").fetchall()
        return [dict(r) for r in rows]

def get_client(client_id):
    with get_connection() as c:
        row = c.execute("SELECT * FROM clients WHERE id=?", (int(client_id),)).fetchone()
        return dict(row) if row else None

def create_client(data):
    name = str(data.get("company_name", "")).strip()
    if not name:
        raise ValueError("Company name is required.")
    values = {k: data.get(k) for k in CLIENT_FIELDS}
    for k, v in list(values.items()):
        if k not in ("monthly_budget",) and v is None:
            values[k] = ""
    values["company_name"] = name
    with get_connection() as c:
        cols = list(values)
        placeholders = ",".join("?" for _ in cols)
        cur = c.execute(f"INSERT INTO clients ({','.join(cols)}) VALUES ({placeholders})",
                        [values[k] for k in cols])
        return cur.lastrowid

def update_client(client_id, data):
    if not str(data.get("company_name", "")).strip():
        raise ValueError("Company name is required.")
    values = {k: data.get(k) for k in CLIENT_FIELDS}
    for k, v in list(values.items()):
        if k not in ("monthly_budget",) and v is None:
            values[k] = ""
    with get_connection() as c:
        cur = c.execute("UPDATE clients SET " + ",".join(f"{k}=?" for k in values) +
                        ", updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        [values[k] for k in values] + [int(client_id)])
        if cur.rowcount == 0:
            raise ValueError("Client not found.")

def delete_client(client_id):
    with get_connection() as c:
        c.execute("DELETE FROM clients WHERE id=?", (int(client_id),))

def client_context(client_id):
    """Reusable, bounded brand context for downstream prompts."""
    client = get_client(client_id)
    if not client:
        raise ValueError("Choose a valid client first.")
    with get_connection() as c:
        accounts = [dict(r) for r in c.execute(
            "SELECT platform,account_status,profile_url,activity_status,followers,posting_frequency,verification_status,notes "
            "FROM social_accounts WHERE client_id=? ORDER BY platform", (int(client_id),)).fetchall()]
    fields = ["company_name","industry","category","location","company_description","products_services",
              "pricing","usp","target_audience","ideal_customer_profile","pain_points","competitors",
              "objectives","preferred_language","brand_voice","brand_guidelines","prohibited_topics"]
    return {"client": {k: client.get(k) for k in fields}, "social_accounts": accounts}
