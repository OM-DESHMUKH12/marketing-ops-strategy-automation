"""Social account assessment services. Unknown is never inferred to mean absent."""
from database.connection import get_connection
PLATFORMS = ["Instagram","Facebook","LinkedIn","YouTube","X","TikTok","Other/custom"]

def list_accounts(client_id):
    with get_connection() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM social_accounts WHERE client_id=? ORDER BY platform", (int(client_id),)).fetchall()]

def upsert_account(client_id, data):
    platform = str(data.get("platform","")).strip()
    if not platform:
        raise ValueError("Platform is required.")
    status = data.get("account_status", "Unknown")
    if status not in ("Present","Absent","Unknown","Not assessed"):
        raise ValueError("Invalid presence status.")
    if status == "Absent" and data.get("profile_url"):
        raise ValueError("An account marked Absent cannot have a profile URL. Use Present or Unknown.")
    fields = ["account_status","profile_url","activity_status","followers","posting_frequency",
              "engagement_metrics","last_reviewed","data_source","verification_status","notes"]
    values = {k:data.get(k) for k in fields}
    for k, v in list(values.items()):
        if k != "followers" and v is None:
            values[k] = ""
    values["activity_status"] = values["activity_status"] or "Unknown"
    values["verification_status"] = values["verification_status"] or "Not verified"
    with get_connection() as c:
        c.execute("""INSERT INTO social_accounts(client_id,platform,account_status,profile_url,activity_status,
            followers,posting_frequency,engagement_metrics,last_reviewed,data_source,verification_status,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(client_id,platform) DO UPDATE SET
            account_status=excluded.account_status, profile_url=excluded.profile_url,
            activity_status=excluded.activity_status, followers=excluded.followers,
            posting_frequency=excluded.posting_frequency, engagement_metrics=excluded.engagement_metrics,
            last_reviewed=excluded.last_reviewed, data_source=excluded.data_source,
            verification_status=excluded.verification_status, notes=excluded.notes,
            updated_at=CURRENT_TIMESTAMP""",
            [int(client_id),platform]+[values[k] for k in fields])

def presence_summary(client_id):
    accounts = list_accounts(client_id)
    statuses = {a["account_status"] for a in accounts}
    return {"accounts":accounts, "has_present": "Present" in statuses,
            "known_absent": "Absent" in statuses, "has_unknown": bool(statuses & {"Unknown","Not assessed"}),
            "assessed_count": sum(a["account_status"] in ("Present","Absent") for a in accounts)}
