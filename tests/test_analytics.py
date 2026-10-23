from services.client_service import create_client
from services.reporting_service import add_metric, analytics_summary, create_report

def test_analytics_use_saved_metrics_only():
    cid=create_client({"company_name":"Analytics Test"})
    before=analytics_summary(cid)
    assert before["impressions"]==0 and before["engagement_rate"] is None
    add_metric({"client_id":cid,"platform":"LinkedIn","period_start":"2026-10-01","period_end":"2026-10-15",
                "reach":100,"impressions":200,"likes":10,"comments":5,"shares":5,"clicks":8,"leads":2,"spend":50})
    s=analytics_summary(cid,"2026-10-01","2026-10-31")
    assert s["reach"]==100
    assert s["interactions"]==20
    assert s["engagement_rate"]==10.0
    assert s["leads"]==2
    rid,report=create_report(cid,"October report","2026-10-01","2026-10-31")
    assert rid and "Recorded impressions: 200" in report
