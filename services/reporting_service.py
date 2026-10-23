"""Analytics from actual saved records only."""
import json
from database.connection import get_connection

def analytics_summary(client_id=None, period_start=None, period_end=None):
    with get_connection() as c:
        where, params = " WHERE 1=1", []
        if client_id: where += " AND client_id=?"; params.append(int(client_id))
        if period_start: where += " AND date(period_end)>=date(?)"; params.append(str(period_start))
        if period_end: where += " AND date(period_start)<=date(?)"; params.append(str(period_end))
        metrics=[dict(r) for r in c.execute("SELECT * FROM performance_metrics"+where+" ORDER BY period_end DESC",params).fetchall()]
        cw, cp = " WHERE 1=1", []
        if client_id: cw += " AND client_id=?"; cp.append(int(client_id))
        content=[dict(r) for r in c.execute("SELECT status,platform,content_type FROM content_items"+cw,cp).fetchall()]
        clients = c.execute("SELECT COUNT(*) n FROM clients").fetchone()["n"]
        if client_id: clients = 1
    reach=sum(m["reach"] for m in metrics)
    impressions=sum(m["impressions"] for m in metrics)
    interactions=sum(m["likes"]+m["comments"]+m["shares"] for m in metrics)
    return {"clients":clients,"content_total":len(content),
        "awaiting_approval":sum(x["status"]=="Pending Approval" for x in content),
        "approved":sum(x["status"]=="Approved" for x in content),
        "scheduled":sum(x["status"]=="Scheduled" for x in content),
        "published":sum(x["status"]=="Published" for x in content),
        "reach":reach,"impressions":impressions,"interactions":interactions,
        "engagement_rate":(interactions/impressions*100 if impressions else None),
        "clicks":sum(m["clicks"] for m in metrics),"leads":sum(m["leads"] for m in metrics),
        "spend":sum(m["spend"] for m in metrics),"metrics":metrics,"content":content}

def add_metric(data):
    if int(data.get("reach",0)) < 0 or int(data.get("impressions",0)) < 0:
        raise ValueError("Reach and impressions cannot be negative.")
    with get_connection() as c:
        cur=c.execute("""INSERT INTO performance_metrics(client_id,content_id,platform,period_start,period_end,
          reach,impressions,likes,comments,shares,clicks,leads,spend,source_label,notes)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (int(data["client_id"]),data.get("content_id") or None,data["platform"],str(data["period_start"]),
           str(data["period_end"]),int(data.get("reach",0)),int(data.get("impressions",0)),
           int(data.get("likes",0)),int(data.get("comments",0)),int(data.get("shares",0)),
           int(data.get("clicks",0)),int(data.get("leads",0)),float(data.get("spend",0)),
           data.get("source_label","Manually entered"),data.get("notes","")))
        return cur.lastrowid

def create_report(client_id, title, period_start, period_end):
    summary=analytics_summary(client_id,period_start,period_end)
    metric_rows=summary["metrics"]
    best = sorted(metric_rows,key=lambda m:m["likes"]+m["comments"]+m["shares"],reverse=True)[:3]
    lines=[
        f"# {title}",f"Reporting period: {period_start} to {period_end}",
        "Data source: saved performance records only; no missing metrics have been imputed.",
        f"Recorded reach: {summary['reach']}",f"Recorded impressions: {summary['impressions']}",
        f"Recorded interactions: {summary['interactions']}",
        ("Engagement rate: %.2f%% (interactions / impressions)" % summary["engagement_rate"]
         if summary["engagement_rate"] is not None else "Engagement rate: unavailable (no recorded impressions)."),
        f"Recorded clicks: {summary['clicks']}",f"Recorded leads: {summary['leads']}",
        f"Recorded spend: {summary['spend']:.2f}",
        "Best-performing recorded metric rows: " + (", ".join(f"{m['platform']} ({m['likes']+m['comments']+m['shares']} interactions)" for m in best) if best else "No performance records in this period."),
        "Recommendations: Validate metric coverage, compare performance by platform and objective, and prioritize experiments that can be measured in the next reporting period."
    ]
    report="\n\n".join(lines)
    with get_connection() as c:
        cur=c.execute("INSERT INTO reports(client_id,title,period_start,period_end,report_text,data_json) VALUES(?,?,?,?,?,?)",
            (int(client_id),title,str(period_start),str(period_end),report,json.dumps({k:v for k,v in summary.items() if k not in ("metrics","content")},default=str)))
        return cur.lastrowid, report

def list_reports(client_id=None):
    with get_connection() as c:
        if client_id:
            rows=c.execute("SELECT * FROM reports WHERE client_id=? ORDER BY created_at DESC",(int(client_id),)).fetchall()
        else:
            rows=c.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
