"""Content persistence and calendar operations."""
import json
from database.connection import get_connection

STATUSES = ["Draft","Pending Approval","Approved","Rejected","Scheduled","Published"]

def list_content(client_id=None, status=None, platform=None, start_date=None, end_date=None):
    sql = """SELECT ci.*, cl.company_name FROM content_items ci JOIN clients cl ON cl.id=ci.client_id WHERE 1=1"""
    params=[]
    if client_id:
        sql += " AND ci.client_id=?"; params.append(int(client_id))
    if status and status != "All":
        sql += " AND ci.status=?"; params.append(status)
    if platform and platform != "All":
        sql += " AND ci.platform=?"; params.append(platform)
    if start_date:
        sql += " AND (ci.scheduled_date IS NULL OR date(ci.scheduled_date)>=date(?))"; params.append(str(start_date))
    if end_date:
        sql += " AND (ci.scheduled_date IS NULL OR date(ci.scheduled_date)<=date(?))"; params.append(str(end_date))
    sql += " ORDER BY CASE WHEN ci.scheduled_date IS NULL THEN 1 ELSE 0 END, ci.scheduled_date, ci.created_at DESC"
    with get_connection() as c:
        return [dict(r) for r in c.execute(sql,params).fetchall()]

def get_content(content_id):
    with get_connection() as c:
        r=c.execute("SELECT * FROM content_items WHERE id=?",(int(content_id),)).fetchone()
        return dict(r) if r else None

def save_content(client_id, data, strategy_id=None, campaign_id=None, scheduled_date=None):
    title = str(data.get("title","")).strip()
    if not title: raise ValueError("Content title is required.")
    payload = dict(data)
    payload.pop("_generation_key",None)
    caption = payload.get("caption","") or ""
    with get_connection() as c:
        # Idempotency on generation request key: a retry does not create a duplicate row.
        key = data.get("_generation_key")
        if key:
            existing = c.execute("SELECT id FROM content_items WHERE generation_key=?",(key,)).fetchone()
            if existing: return existing["id"]
        cur=c.execute("""INSERT INTO content_items(client_id,strategy_id,campaign_id,title,platform,content_type,topic,
            objective,caption,content_json,scheduled_date,status,approval_status,generation_key)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (int(client_id),strategy_id,campaign_id,title,data.get("platform","Other"),
             data.get("content_type","Social post"),data.get("topic",""),data.get("objective",""),
             caption,json.dumps(payload,ensure_ascii=False),str(scheduled_date) if scheduled_date else None,
             "Draft","Not submitted",key))
        cid=cur.lastrowid
        c.execute("INSERT INTO content_revisions(content_id,revision_number,content_json,comment) VALUES(?,?,?,?)",
                  (cid,1,json.dumps(payload,ensure_ascii=False),"Initial draft"))
        return cid

def update_content(content_id, title, platform, content_type, topic, caption, content_json, scheduled_date=None):
    current=get_content(content_id)
    if not current: raise ValueError("Content item not found.")
    payload = content_json if isinstance(content_json,dict) else json.loads(content_json or "{}")
    payload.update({"title":title,"platform":platform,"content_type":content_type,"topic":topic,"caption":caption})
    with get_connection() as c:
        c.execute("""UPDATE content_items SET title=?,platform=?,content_type=?,topic=?,caption=?,content_json=?,
            scheduled_date=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
            (title,platform,content_type,topic,caption,json.dumps(payload,ensure_ascii=False),
             str(scheduled_date) if scheduled_date else None,int(content_id)))
        revision = c.execute("SELECT COALESCE(MAX(revision_number),0)+1 n FROM content_revisions WHERE content_id=?",
                             (int(content_id),)).fetchone()["n"]
        c.execute("INSERT INTO content_revisions(content_id,revision_number,content_json,comment) VALUES(?,?,?,?)",
                  (int(content_id),revision,json.dumps(payload,ensure_ascii=False),"Edited in content studio/calendar"))

def delete_content(content_id):
    with get_connection() as c:
        c.execute("DELETE FROM content_items WHERE id=?",(int(content_id),))

def schedule_content(content_id, scheduled_date):
    item=get_content(content_id)
    if not item: raise ValueError("Content item not found.")
    if item["status"] != "Approved":
        raise ValueError("Only approved content can be marked Scheduled. Submit and approve it first.")
    if not scheduled_date: raise ValueError("Choose a schedule date.")
    with get_connection() as c:
        c.execute("UPDATE content_items SET scheduled_date=?,status='Scheduled',updated_at=CURRENT_TIMESTAMP WHERE id=?",
                  (str(scheduled_date),int(content_id)))
        c.execute("INSERT OR IGNORE INTO schedules(content_id,scheduled_for,status) VALUES(?,?,?)",
                  (int(content_id),str(scheduled_date),"Ready for external scheduling"))
