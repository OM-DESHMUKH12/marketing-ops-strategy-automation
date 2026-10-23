"""Explicit human approval and revision state transitions."""
from database.connection import get_connection
from services.content_service import get_content

ALLOWED = {
 "Draft":{"Pending Approval"},
 "Pending Approval":{"Approved","Rejected","Draft"},
 "Rejected":{"Draft"},
 "Approved":{"Draft","Scheduled"},
 "Scheduled":{"Approved"},
 "Published":set(),
}

def transition(content_id, new_status, comment="", reviewer="Agency reviewer"):
    item=get_content(content_id)
    if not item: raise ValueError("Content item not found.")
    old=item["status"]
    if new_status not in ALLOWED.get(old,set()):
        raise ValueError(f"Invalid status transition: {old} → {new_status}.")
    if new_status in ("Approved","Rejected") and not comment.strip() and new_status=="Rejected":
        raise ValueError("Add a revision comment when rejecting content.")
    with get_connection() as c:
        c.execute("UPDATE content_items SET status=?,approval_status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                  (new_status, new_status if new_status in ("Approved","Rejected","Pending Approval") else item["approval_status"],int(content_id)))
        if new_status in ("Approved","Rejected","Pending Approval"):
            c.execute("INSERT INTO approvals(content_id,decision,comment,reviewer) VALUES(?,?,?,?)",
                      (int(content_id),new_status,comment.strip(),reviewer.strip() or "Agency reviewer"))
        if new_status=="Published":
            raise ValueError("Publishing requires a configured external integration and confirmed evidence. This beta does not publish content.")

def approval_history(content_id):
    with get_connection() as c:
        return [dict(r) for r in c.execute("SELECT * FROM approvals WHERE content_id=? ORDER BY created_at DESC",(int(content_id),)).fetchall()]
