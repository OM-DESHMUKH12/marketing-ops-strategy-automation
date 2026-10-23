"""Marketing Operations — Streamlit beta app."""
import os, json, traceback
from datetime import date, timedelta
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from database.connection import init_db
from services import client_service, presence_service, content_service, approval_service, reporting_service
from ai.ollama_client import connection_status, ollama_settings, OllamaError
from ai.strategy_generator import generate_strategy, list_strategies
from ai.content_generator import generate_content, generate_calendar_batch
from ai.content_reviewer import review_content
from ai.context_builder import build_context
from workflows.content_workflow import generate_and_save
from integrations.social_platforms import integration_status
from integrations.huggingface_images import generate_image, ImageGenerationError

load_dotenv()
init_db()
st.set_page_config(page_title="Marketing Operations", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --navy:#10243A; --blue:#326CE5; }
[data-testid="stAppViewContainer"] { background: #F6F8FB; }
[data-testid="stSidebar"] { background: #10243A; }
[data-testid="stSidebar"] * { color: #F7FAFF !important; }
h1,h2,h3 { color:#10243A; }
[data-testid="stMetric"] { background:white; padding:16px; border:1px solid #E4EAF2; border-radius:12px; }
div[data-testid="stForm"] { background:white; padding:12px; border-radius:12px; }
.small-muted {color:#65758B; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

def safe_error(prefix, exc):
    st.error(f"{prefix}: {exc}")
    st.caption("No external publishing was attempted. Check the relevant Settings or troubleshooting instructions.")

def clients():
    return client_service.list_clients()

def client_select(label="Client", key="client_select", allow_all=False):
    cs=clients()
    if not cs:
        st.info("No clients yet. Open **Clients** to create one or load sample clients.")
        return None
    options=({"All clients":None} if allow_all else {})
    options.update({f"{c['company_name']} · #{c['id']}":c["id"] for c in cs})
    chosen=st.selectbox(label,list(options),key=key)
    return options[chosen]

def render_dashboard():
    st.title("Marketing operations overview")
    st.caption("Your agency workspace for client intelligence, AI-assisted planning, content approvals and recorded performance.")
    status=connection_status()
    if status["connected"] and status["model_found"]:
        st.success(f"Local AI ready · {status['model']}")
    else:
        st.warning("Local AI is not ready. Client management, calendar, approvals and saved analytics remain available.")
        st.caption(status["message"])
    summary=reporting_service.analytics_summary()
    a,b,c,d=st.columns(4)
    a.metric("Clients",summary["clients"]); b.metric("Content drafts",summary["content_total"])
    c.metric("Awaiting approval",summary["awaiting_approval"]); d.metric("Scheduled",summary["scheduled"])
    st.subheader("Workflow")
    st.markdown("**Onboard client → Audit presence → Generate strategy → Create content → Review and approve → Schedule → Record results**")
    left,right=st.columns([1.2,1])
    with left:
        st.subheader("Recent content")
        rows=content_service.list_content()
        if rows:
            st.dataframe(pd.DataFrame(rows)[["title","company_name","platform","content_type","scheduled_date","status"]].head(8),
                         use_container_width=True, hide_index=True)
        else: st.info("No content saved yet. Generate a draft in AI Content Studio.")
    with right:
        st.subheader("Status distribution")
        if summary["content"]:
            df=pd.DataFrame(summary["content"]).groupby("status",as_index=False).size()
            st.plotly_chart(px.pie(df,names="status",values="size",hole=.55),use_container_width=True)
        else: st.info("Status charts appear after content is saved.")
    st.caption("Published totals include only items explicitly recorded as Published. This beta does not connect to publishing APIs.")

def render_clients():
    st.title("Clients")
    st.caption("Create and maintain a reusable company and brand profile.")
    with st.expander("＋ Add client",expanded=not bool(clients())):
        with st.form("new_client_form"):
            a,b=st.columns(2)
            with a:
                name=st.text_input("Company name *")
                industry=st.text_input("Industry")
                category=st.text_input("Business category")
                website=st.text_input("Website URL")
                website_status=st.selectbox("Website status",["Unknown","Present","Absent","Present (user supplied; not fetched)"])
                location=st.text_input("Business location")
                description=st.text_area("Company description")
                products=st.text_area("Products and services")
                pricing=st.text_input("Pricing (optional)")
                usp=st.text_area("Unique selling proposition")
            with b:
                audience=st.text_area("Target audience")
                icp=st.text_area("Ideal customer profile")
                pain=st.text_area("Customer pain points")
                competitors=st.text_area("Competitors (user supplied; no research performed)")
                objectives=st.text_area("Business objectives")
                budget=st.number_input("Monthly marketing budget",min_value=0.0,value=0.0,step=1000.0)
                language=st.selectbox("Preferred language",["English","Hindi","Marathi","Other"])
                voice=st.selectbox("Brand voice",["Professional","Technical and trustworthy","Energetic and approachable","Friendly","Premium","Educational","Custom"])
                guidelines=st.text_area("Brand guidelines")
                prohibited=st.text_area("Prohibited claims or topics")
                contact=st.text_input("Contact details (optional)")
            submitted=st.form_submit_button("Create client",type="primary")
        if submitted:
            try:
                cid=client_service.create_client({"company_name":name,"industry":industry,"category":category,
                    "website_url":website,"website_status":website_status,"location":location,
                    "company_description":description,"products_services":products,"pricing":pricing,"usp":usp,
                    "target_audience":audience,"ideal_customer_profile":icp,"pain_points":pain,
                    "competitors":competitors,"objectives":objectives,"monthly_budget":budget or None,
                    "preferred_language":language,"brand_voice":voice,"brand_guidelines":guidelines,
                    "prohibited_topics":prohibited,"contact_details":contact})
                st.success(f"Created client #{cid}."); st.rerun()
            except Exception as e: safe_error("Could not create client",e)
    st.subheader("Client directory")
    query=st.text_input("Search by company, industry or location",key="client_search")
    rows=client_service.list_clients(query)
    if not rows:
        st.info("No matching clients. Create one above or use sample clients from Settings.")
        return
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    ids={f"{r['company_name']} · #{r['id']}":r["id"] for r in rows}
    selected=st.selectbox("Edit or view client",list(ids),key="client_edit_select")
    cid=ids[selected]; current=client_service.get_client(cid)
    with st.expander("Edit selected client"):
        with st.form(f"edit_client_{cid}"):
            name=st.text_input("Company name *",current["company_name"])
            industry=st.text_input("Industry",current["industry"])
            category=st.text_input("Business category",current["category"])
            website=st.text_input("Website URL",current["website_url"])
            website_status=st.selectbox("Website status",["Unknown","Present","Absent","Present (user supplied; not fetched)"],
                index=["Unknown","Present","Absent","Present (user supplied; not fetched)"].index(current.get("website_status","Unknown")))
            location=st.text_input("Location",current["location"])
            description=st.text_area("Company description",current["company_description"])
            products=st.text_area("Products and services",current["products_services"])
            pricing=st.text_input("Pricing",current["pricing"]); usp=st.text_area("USP",current["usp"])
            audience=st.text_area("Target audience",current["target_audience"])
            icp=st.text_area("Ideal customer profile",current["ideal_customer_profile"])
            pain=st.text_area("Customer pain points",current["pain_points"])
            competitors=st.text_area("Competitors",current["competitors"])
            objectives=st.text_area("Business objectives",current["objectives"])
            budget=st.number_input("Monthly budget",min_value=0.0,value=float(current["monthly_budget"] or 0))
            language=st.text_input("Preferred language",current["preferred_language"])
            voice=st.text_input("Brand voice",current["brand_voice"])
            guidelines=st.text_area("Brand guidelines",current["brand_guidelines"])
            prohibited=st.text_area("Prohibited claims/topics",current["prohibited_topics"])
            contact=st.text_input("Contact details",current["contact_details"])
            save=st.form_submit_button("Save changes",type="primary")
        if save:
            try:
                client_service.update_client(cid,{"company_name":name,"industry":industry,"category":category,
                    "website_url":website,"website_status":website_status,"location":location,
                    "company_description":description,"products_services":products,"pricing":pricing,"usp":usp,
                    "target_audience":audience,"ideal_customer_profile":icp,"pain_points":pain,
                    "competitors":competitors,"objectives":objectives,"monthly_budget":budget or None,
                    "preferred_language":language,"brand_voice":voice,"brand_guidelines":guidelines,
                    "prohibited_topics":prohibited,"contact_details":contact})
                st.success("Client updated."); st.rerun()
            except Exception as e: safe_error("Could not update client",e)
    with st.expander("Delete selected client"):
        st.warning("This permanently deletes the client and its related accounts, strategies, content and metrics.")
        confirm=st.checkbox(f"I understand — delete {current['company_name']}",key=f"confirm_del_{cid}")
        if st.button("Delete client",disabled=not confirm,key=f"del_client_{cid}"):
            client_service.delete_client(cid); st.success("Client deleted."); st.rerun()

def render_presence():
    st.title("Digital presence audit")
    st.caption("Track account existence, activity and evidence separately. Empty URLs do not mean an account is absent.")
    cid=client_select(key="presence_client")
    if cid is None:return
    existing=presence_service.list_accounts(cid)
    st.subheader("Current assessment")
    if existing:
        st.dataframe(pd.DataFrame(existing)[["platform","account_status","profile_url","activity_status","followers","posting_frequency","verification_status","last_reviewed","data_source"]],
                     use_container_width=True,hide_index=True)
    else: st.info("No platform assessments recorded for this client.")
    st.subheader("Add or update a platform")
    with st.form("presence_form"):
        platform=st.selectbox("Platform",presence_service.PLATFORMS)
        account_status=st.selectbox("Account existence",["Unknown","Not assessed","Present","Absent"],
            help="Use Absent only when assessed. Unknown and Not assessed are not the same as Absent.")
        url=st.text_input("Profile URL (optional)")
        activity=st.selectbox("Account activity",["Unknown","Active","Inactive","Not assessed"])
        followers=st.number_input("Followers/subscribers (if known)",min_value=0,value=0)
        frequency=st.text_input("Posting frequency (e.g. 2 posts/week)")
        engagement=st.text_input("Engagement metrics (if available)")
        reviewed=st.date_input("Last reviewed",value=date.today())
        source=st.text_input("Data source (e.g. client supplied URL, manual review)")
        verification=st.selectbox("Verification status",["Not verified","Client supplied","Manually reviewed","Trusted source checked"])
        notes=st.text_area("Notes")
        save=st.form_submit_button("Save assessment",type="primary")
    if save:
        try:
            presence_service.upsert_account(cid,{"platform":platform,"account_status":account_status,
                "profile_url":url,"activity_status":activity,"followers":followers or None,
                "posting_frequency":frequency,"engagement_metrics":engagement,"last_reviewed":str(reviewed),
                "data_source":source,"verification_status":verification,"notes":notes})
            st.success("Presence assessment saved."); st.rerun()
        except Exception as e: safe_error("Could not save assessment",e)
    st.info(integration_status()["message"])

def render_strategy():
    st.title("Marketing strategy")
    st.caption("Generate a strategy from the selected client's saved brand profile and presence assessment.")
    cid=client_select(key="strategy_client")
    if cid is None:return
    client=client_service.get_client(cid)
    with st.form("strategy_form"):
        objective=st.selectbox("Campaign objective",["Generate qualified enquiries","Brand awareness","Website traffic","Community growth","Trial bookings","Thought leadership","Product launch","Retention"])
        duration=st.selectbox("Duration", [7,14,30,60,90],index=2)
        platforms=st.multiselect("Preferred platforms",presence_service.PLATFORMS,default=[])
        frequency=st.selectbox("Posting frequency",["2 posts/week","3 posts/week","5 posts/week","Daily","Custom"])
        theme=st.text_input("Campaign theme")
        budget=st.number_input("Optional campaign budget",min_value=0.0,value=float(client.get("monthly_budget") or 0))
        instructions=st.text_area("Additional instructions")
        go=st.form_submit_button("Generate strategy with local AI",type="primary")
    if go:
        with st.spinner("Generating with local Ollama model…"):
            try:
                result=generate_strategy(cid,{"objective":objective,"duration_days":duration,"platforms":platforms,
                    "frequency":frequency,"theme":theme,"budget":budget,"instructions":instructions})
                st.session_state["last_strategy_id"]=result["_id"]
                st.success("Strategy generated and saved.")
                st.session_state["strategy_result"]=result
            except Exception as e: safe_error("Strategy generation failed",e)
    result=st.session_state.get("strategy_result")
    if result:
        st.subheader("Generated strategy")
        st.markdown(result.get("executive_summary",""))
        for title,key in [("Business understanding","business_understanding"),("Objectives","objectives"),
                          ("Recommended platforms","recommended_platforms"),("Content pillars","content_pillars"),
                          ("Messaging","messaging"),("Campaign ideas","campaign_ideas"),
                          ("Posting frequency","posting_frequency"),("30-day roadmap","roadmap_30_days"),
                          ("KPIs","kpis"),("Risks, assumptions and missing information","risks_assumptions_missing_info")]:
            with st.expander(title,expanded=title in ("Objectives","Recommended platforms","30-day roadmap")):
                val=result.get(key)
                st.write(val if val else "Not provided.")
    st.subheader("Saved strategies")
    saved=list_strategies(cid)
    if saved:
        for s in saved:
            with st.expander(f"{s['title']} · {s['created_at']}"):
                st.write(f"Objective: {s['objective']}")
                try: st.json(json.loads(s["strategy_json"]))
                except Exception: st.write(s["strategy_json"])
    else: st.caption("No saved strategies yet.")

def render_content_studio():
    st.title("AI content studio")
    st.caption("Generate real drafts through your configured local Ollama model. Nothing is published automatically.")
    cid=client_select(key="content_client")
    if cid is None:return
    saved_strategies=list_strategies(cid)
    strategy_options={"No linked strategy":None}
    strategy_options.update({f"{s['title']} · #{s['id']}":s["id"] for s in saved_strategies})
    with st.form("content_gen_form"):
        strategy_label=st.selectbox("Saved strategy (optional)",list(strategy_options))
        platform=st.selectbox("Platform",presence_service.PLATFORMS)
        content_type=st.selectbox("Content type",["Social post","Instagram carousel","Reel / short-form video","LinkedIn thought leadership","Campaign content"])
        topic=st.text_area("Topic or brief",placeholder="e.g. Explain how OEM buyers can evaluate a precision component supplier")
        objective=st.text_input("Marketing objective",value="Generate qualified enquiries")
        tone=st.text_input("Tone override (optional)",value="Use saved brand voice")
        language=st.text_input("Language override",value="Use saved preferred language")
        generate_btn=st.form_submit_button("Generate draft",type="primary")
    if generate_btn:
        options={"strategy_id":strategy_options[strategy_label],"platform":platform,"content_type":content_type,
                 "topic":topic,"objective":objective,"tone":tone,"language":language}
        with st.spinner("Waiting for local model inference…"):
            try:
                draft=generate_content(cid,options)
                st.session_state["generated_draft"]=draft
                st.session_state["generated_client_id"]=cid
                st.success("AI draft generated. Review and save it below.")
            except Exception as e: safe_error("Content generation failed",e)
    draft=st.session_state.get("generated_draft")
    if draft and st.session_state.get("generated_client_id")==cid:
        st.subheader("Review and edit generated draft")
        with st.form("draft_edit_form"):
            title=st.text_input("Title",draft.get("title",""))
            caption=st.text_area("Caption / main copy",draft.get("caption",""),height=220)
            hook=st.text_area("Hook",draft.get("hook",""))
            cta=st.text_input("Call to action",draft.get("call_to_action",""))
            hashtags=st.text_input("Hashtags (comma separated)",", ".join(draft.get("hashtags",[])))
            visual=st.text_area("Suggested visual",draft.get("suggested_visual",""))
            creative=st.text_area("Creative brief",draft.get("creative_brief",""))
            if draft.get("carousel_slides"): st.json(draft["carousel_slides"])
            if draft.get("video_scenes"): st.json(draft["video_scenes"])
            save_draft=st.form_submit_button("Save draft",type="primary")
        if save_draft:
            updated=dict(draft); updated.update({"title":title,"caption":caption,"hook":hook,"call_to_action":cta,
                "hashtags":[h.strip() for h in hashtags.split(",") if h.strip()],"suggested_visual":visual,"creative_brief":creative})
            try:
                cid_saved=content_service.save_content(cid,updated,strategy_id=strategy_options[strategy_label])
                st.success(f"Saved as content item #{cid_saved}.")
                st.session_state.pop("generated_draft",None)
            except Exception as e: safe_error("Could not save draft",e)
    st.divider()
    st.subheader("Cloud image studio · Hugging Face")
    st.caption("Generates an image using the public Stable Diffusion 3.5 Large Space. Availability and free quota are controlled by Hugging Face; generated product details may be inaccurate.")
    current_draft = st.session_state.get("generated_draft")
    draft_for_client = current_draft if current_draft and st.session_state.get("generated_client_id") == cid else None
    suggested_prompt = ""
    if draft_for_client:
        suggested_prompt = (draft_for_client.get("suggested_visual") or draft_for_client.get("creative_brief") or "").strip()
    with st.form("hf_image_form"):
        image_prompt = st.text_area("Image prompt", value=suggested_prompt, height=130,
            placeholder="Describe the scene, composition, lighting, brand mood and intended audience. Avoid asking the model to render exact text or logos.")
        negative_prompt = st.text_input("Negative prompt", value="blurry, low quality, distorted geometry, malformed product, watermark, text")
        image_col1, image_col2, image_col3 = st.columns(3)
        image_width = image_col1.selectbox("Width", [512, 768, 1024], index=2)
        image_height = image_col2.selectbox("Height", [512, 768, 1024], index=2)
        image_steps = image_col3.selectbox("Inference steps", [20, 30, 40], index=2)
        image_guidance = st.slider("Prompt guidance", min_value=1.0, max_value=10.0, value=4.5, step=0.5)
        make_image = st.form_submit_button("Generate image", type="primary")
    if make_image:
        with st.spinner("Contacting Hugging Face Space. This may take a few minutes if there is a queue…"):
            try:
                generated_path = generate_image(image_prompt, negative_prompt, image_width, image_height,
                    image_guidance, image_steps)
                st.session_state["hf_generated_image_path"] = str(generated_path)
                st.session_state["hf_generated_image_client_id"] = cid
                st.success("Image generated and saved locally.")
            except (ImageGenerationError, ValueError) as e:
                safe_error("Image generation failed", e)
            except Exception as e:
                safe_error("Unexpected image generation error", e)
    image_path_value = st.session_state.get("hf_generated_image_path")
    if image_path_value and st.session_state.get("hf_generated_image_client_id") == cid:
        image_file = Path(image_path_value)
        if image_file.is_file():
            st.image(str(image_file), caption="AI-generated image — verify product accuracy before publishing.", use_container_width=True)
            st.download_button("Download PNG/image", data=image_file.read_bytes(), file_name=image_file.name,
                mime="image/png" if image_file.suffix.lower() == ".png" else "image/jpeg")

    st.divider()
    st.subheader("Existing drafts")
    items=content_service.list_content(client_id=cid)
    if items:
        st.dataframe(pd.DataFrame(items)[["id","title","platform","content_type","scheduled_date","status","created_at"]],
                     use_container_width=True,hide_index=True)
    else: st.info("No content for this client yet.")

def render_calendar():
    st.title("Content calendar")
    st.caption("Turn a saved strategy into dated post briefs, captions and image prompts. Content is saved as drafts for human review; this does not publish automatically.")
    cid=client_select(key="calendar_client",allow_all=True)
    if not clients(): return

    # Strategy-to-calendar automation: one planned post becomes one saved draft with its own visual prompt.
    if cid is not None:
        st.subheader("⚡ Automate a week or month of content")
        st.caption("Choose a saved strategy and the system will create a dated content brief for each posting slot, including a platform-specific caption and image-generation prompt.")
        strategy_rows=list_strategies(cid)
        if not strategy_rows:
            st.info("Generate and save a strategy in Marketing Strategy first. Then return here to turn it into a content calendar.")
        else:
            strategy_opts={f"{row['title']} · #{row['id']} · {row['created_at']}":row for row in strategy_rows}
            with st.form("strategy_calendar_automation"):
                chosen_strategy_label=st.selectbox("Strategy to operationalize",list(strategy_opts))
                chosen_strategy=strategy_opts[chosen_strategy_label]
                strategy_data={}
                try: strategy_data=json.loads(chosen_strategy.get("strategy_json") or "{}")
                except Exception: pass
                recommended=[]
                for p in strategy_data.get("recommended_platforms",[]) or []:
                    if isinstance(p,dict) and p.get("platform") in presence_service.PLATFORMS and p.get("platform") not in recommended:
                        recommended.append(p.get("platform"))
                chosen_platforms=st.multiselect("Platforms",presence_service.PLATFORMS,default=recommended[:2] or ["LinkedIn"] if "LinkedIn" in presence_service.PLATFORMS else recommended[:2])
                start_day=st.date_input("Start date",value=date.today()+timedelta(days=1),key="automation_start_date")
                duration_days=st.selectbox("Planning window",[7,14,30],index=2)
                posts_per_week=st.selectbox("Posting frequency",[2,3,5,7],index=1,format_func=lambda n:{2:"2 posts/week",3:"3 posts/week",5:"5 posts/week",7:"Daily"}[n])
                create_images=st.checkbox("Also generate an image for every post now (uses Hugging Face quota)",value=False)
                submit_plan=st.form_submit_button("Generate calendar drafts + image prompts",type="primary")
            if submit_plan:
                if not chosen_platforms:
                    st.error("Select at least one platform.")
                else:
                    # Spread post slots across the requested window, avoiding a burst of posts on one day.
                    slot_count=max(1, min(duration_days, round(duration_days*posts_per_week/7)))
                    dates=[start_day+timedelta(days=round(i*(duration_days-1)/max(1,slot_count-1))) for i in range(slot_count)]
                    pillars=strategy_data.get("content_pillars",[]) or []
                    ideas=strategy_data.get("campaign_ideas",[]) or []
                    slots=[]
                    for idx,post_date in enumerate(dates):
                        platform=chosen_platforms[idx % len(chosen_platforms)]
                        pillar=pillars[idx % len(pillars)] if pillars else "Product education and buyer guidance"
                        idea=ideas[idx % len(ideas)] if ideas else {}
                        if isinstance(idea,dict): idea_text=idea.get("idea") or idea.get("title") or idea.get("concept") or str(idea)
                        else: idea_text=str(idea)
                        slots.append({"date":post_date.isoformat(),"platform":platform,"pillar":pillar,"idea":idea_text})

                    created=[]; failures=[]
                    batch_size=3
                    batches=[slots[i:i+batch_size] for i in range(0,len(slots),batch_size)]
                    progress=st.progress(0, text=f"Preparing {len(slots)} posts in {len(batches)} small AI batches…")
                    for batch_idx,batch in enumerate(batches):
                        try:
                            drafts=generate_calendar_batch(
                                cid, chosen_strategy["id"], batch,
                                objective=chosen_strategy.get("objective") or "Generate qualified enquiries")
                            # Persist each successful batch immediately so later failures do not lose earlier work.
                            for slot,draft in zip(batch,drafts):
                                post_date=date.fromisoformat(slot["date"])
                                draft["campaign_plan"]={"strategy_id":chosen_strategy["id"],"window_days":duration_days,
                                    "slot_number":slots.index(slot)+1,"slot_count":slot_count,"content_pillar":slot["pillar"],"platform":slot["platform"]}
                                content_id=content_service.save_content(cid,draft,strategy_id=chosen_strategy["id"],scheduled_date=post_date)
                                created.append({"id":content_id,"date":post_date.isoformat(),"platform":slot["platform"],
                                    "title":draft.get("title","Untitled"),"image_prompt":draft.get("image_prompt","")})
                            if create_images:
                                for item in created[-len(batch):]:
                                    visual=item.get("image_prompt","")
                                    if visual:
                                        try:
                                            image_path=generate_image(visual,width=512,height=512,guidance_scale=4.5,steps=20)
                                            item["generated_image_path"]=str(image_path)
                                            saved=content_service.get_content(item["id"])
                                            if saved:
                                                payload=json.loads(saved.get("content_json") or "{}")
                                                payload["generated_image_path"]=str(image_path)
                                                content_service.update_content(item["id"],saved["title"],saved["platform"],saved["content_type"],
                                                    saved["topic"],saved["caption"],payload,saved.get("scheduled_date"))
                                        except Exception as image_exc:
                                            failures.append(f"Post {item['id']}: draft saved, image failed — {str(image_exc)[:180]}")
                        except Exception as exc:
                            failed_range=f"posts {slots.index(batch[0])+1}-{slots.index(batch[-1])+1}"
                            failures.append(f"Batch {batch_idx+1} ({failed_range}): {str(exc)[:220]}")
                        progress.progress((batch_idx+1)/len(batches), text=f"Processed batch {batch_idx+1} of {len(batches)}; {len(created)} drafts saved…")

                    if created:
                        st.success(f"Created {len(created)} content drafts from the strategy. Each draft includes its own visual prompt and proposed date.")
                        st.dataframe(pd.DataFrame(created)[["id","date","platform","title"]],use_container_width=True,hide_index=True)
                        st.session_state["calendar_automation_created"]=created
                    if failures:
                        st.warning("Some steps need attention. Successfully saved drafts have been preserved:")
                        for message in failures: st.write("- "+message)
                    st.info("Drafts are not approved or published automatically. Review them in Approvals before scheduling. Image generation can use free Space quota and may queue/fail.")
        st.divider()

    a,b,c=st.columns(3)
    status=a.selectbox("Status",["All"]+content_service.STATUSES,key="calendar_status")
    platform=b.selectbox("Platform",["All"]+presence_service.PLATFORMS,key="calendar_platform")
    start=c.date_input("From",value=date.today()-timedelta(days=14),key="calendar_start")
    end=st.date_input("To",value=date.today()+timedelta(days=30),key="calendar_end")
    items=content_service.list_content(client_id=cid,status=status,platform=platform,start_date=start,end_date=end)
    if items:
        st.dataframe(pd.DataFrame(items)[["id","company_name","title","platform","content_type","scheduled_date","status"]],
                     use_container_width=True,hide_index=True)
    else: st.info("No content matches these filters.")
    st.subheader("Manage content item")
    all_items=content_service.list_content(client_id=cid)
    if not all_items: return
    item_opts={f"#{x['id']} · {x['company_name']} · {x['title']}":x["id"] for x in all_items}
    selected=st.selectbox("Choose item",list(item_opts),key="calendar_item")
    item=content_service.get_content(item_opts[selected])
    with st.form("calendar_edit"):
        title=st.text_input("Title",item["title"])
        item_platform=st.selectbox("Platform",presence_service.PLATFORMS,
            index=presence_service.PLATFORMS.index(item["platform"]) if item["platform"] in presence_service.PLATFORMS else 0)
        item_type=st.text_input("Format",item["content_type"])
        topic=st.text_input("Topic",item["topic"])
        caption=st.text_area("Caption / copy",item["caption"],height=140)
        schedule_date=st.date_input("Proposed date",value=date.fromisoformat(item["scheduled_date"][:10]) if item["scheduled_date"] else date.today()+timedelta(days=1))
        save=st.form_submit_button("Save edits")
    if save:
        try:
            content_service.update_content(item["id"],title,item_platform,item_type,topic,caption,item["content_json"],schedule_date)
            st.success("Content updated; a revision record was saved."); st.rerun()
        except Exception as e: safe_error("Could not update content",e)
    x,y,z=st.columns(3)
    with x:
        if st.button("Duplicate as draft",key=f"duplicate_{item['id']}"):
            payload=json.loads(item["content_json"]); payload["title"]=item["title"]+" (copy)"; payload.pop("_generation_key",None)
            new_id=content_service.save_content(item["client_id"],payload,strategy_id=item["strategy_id"],campaign_id=item["campaign_id"])
            st.success(f"Duplicated as draft #{new_id}."); st.rerun()
    with y:
        if item["status"]=="Approved":
            if st.button("Mark Scheduled",key=f"schedule_{item['id']}"):
                try: content_service.schedule_content(item["id"],schedule_date); st.success("Marked ready for external scheduling."); st.rerun()
                except Exception as e: safe_error("Could not schedule",e)
        else: st.button("Mark Scheduled",disabled=True,key=f"schedule_disabled_{item['id']}",help="Only approved items can be scheduled.")
    with z:
        confirm=st.checkbox("Confirm deletion",key=f"confirm_content_delete_{item['id']}")
        if st.button("Delete item",disabled=not confirm,key=f"delete_content_{item['id']}"):
            content_service.delete_content(item["id"]); st.success("Deleted."); st.rerun()
    st.caption("No publishing API is connected. Scheduled status means the item is prepared for an external scheduling step.")

def render_approvals():
    st.title("Approvals")
    st.caption("Every approval is an explicit human decision. Approval history is retained.")
    cid=client_select(key="approval_client",allow_all=True)
    if not clients():return
    items=content_service.list_content(client_id=cid)
    queue=[x for x in items if x["status"] in ("Pending Approval","Rejected","Approved","Draft")]
    if not queue: st.info("No drafts or approval requests found.")
    else:
        st.dataframe(pd.DataFrame(queue)[["id","company_name","title","platform","status","updated_at"]],
                     use_container_width=True,hide_index=True)
        opts={f"#{x['id']} · {x['company_name']} · {x['title']} [{x['status']}]":x["id"] for x in queue}
        chosen=st.selectbox("Review item",list(opts),key="approval_item")
        item=content_service.get_content(opts[chosen])
        st.subheader(item["title"]); st.write(item["caption"])
        with st.expander("Full generated content"):
            try: st.json(json.loads(item["content_json"]))
            except Exception: st.write(item["content_json"])
        reviewer=st.text_input("Reviewer name",value="Agency reviewer")
        comment=st.text_area("Review note / revision request",key=f"approval_comment_{item['id']}")
        p,q,r=st.columns(3)
        with p:
            if item["status"] in ("Draft","Rejected"):
                if st.button("Submit for approval",key=f"submit_{item['id']}"):
                    try: approval_service.transition(item["id"],"Pending Approval",comment,reviewer); st.success("Submitted for approval."); st.rerun()
                    except Exception as e: safe_error("Transition failed",e)
        with q:
            if item["status"]=="Pending Approval":
                if st.button("Approve",type="primary",key=f"approve_{item['id']}"):
                    try: approval_service.transition(item["id"],"Approved",comment,reviewer); st.success("Approved."); st.rerun()
                    except Exception as e: safe_error("Approval failed",e)
        with r:
            if item["status"]=="Pending Approval":
                if st.button("Reject / request revision",key=f"reject_{item['id']}"):
                    try: approval_service.transition(item["id"],"Rejected",comment,reviewer); st.success("Rejected with revision note."); st.rerun()
                    except Exception as e: safe_error("Rejection failed",e)
        if item["status"]=="Approved":
            if st.button("Return to draft (material revision)",key=f"return_draft_{item['id']}"):
                try: approval_service.transition(item["id"],"Draft",comment,reviewer); st.success("Returned to draft; reapproval is required."); st.rerun()
                except Exception as e: safe_error("Transition failed",e)
        history=approval_service.approval_history(item["id"])
        if history:
            with st.expander("Approval history"):
                st.dataframe(pd.DataFrame(history),use_container_width=True,hide_index=True)

def render_reports():
    st.title("Analytics and reports")
    st.caption("Only saved metric records are counted. Empty datasets remain empty; no results are fabricated.")
    cid=client_select(key="report_client",allow_all=True)
    if not clients():return
    start=st.date_input("Reporting period start",value=date.today()-timedelta(days=30),key="report_start")
    end=st.date_input("Reporting period end",value=date.today(),key="report_end")
    summary=reporting_service.analytics_summary(cid,start,end)
    a,b,c,d=st.columns(4)
    a.metric("Recorded reach",f"{summary['reach']:,}")
    b.metric("Impressions",f"{summary['impressions']:,}")
    c.metric("Interactions",f"{summary['interactions']:,}")
    d.metric("Engagement rate",f"{summary['engagement_rate']:.2f}%" if summary["engagement_rate"] is not None else "N/A")
    x,y,z=st.columns(3)
    x.metric("Clicks",summary["clicks"]); y.metric("Leads",summary["leads"]); z.metric("Recorded spend",f"{summary['spend']:,.2f}")
    if summary["metrics"]:
        df=pd.DataFrame(summary["metrics"])
        byplat=df.groupby("platform",as_index=False)[["reach","impressions","likes","comments","shares","clicks","leads"]].sum()
        st.plotly_chart(px.bar(byplat,x="platform",y=["reach","impressions"],barmode="group",title="Recorded reach and impressions by platform"),use_container_width=True)
        st.plotly_chart(px.bar(byplat,x="platform",y=["likes","comments","shares"],barmode="group",title="Recorded interactions by platform"),use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
    else: st.info("No performance metrics recorded for this period. Add actual numbers below; charts will appear once saved.")
    st.subheader("Enter platform metrics")
    with st.form("metric_form"):
        metric_client=cid
        if cid is None:
            metric_client=client_select("Client for metric","metric_client")
        metric_platform=st.selectbox("Platform",presence_service.PLATFORMS)
        m1,m2=st.columns(2)
        with m1:
            ps=st.date_input("Metric period start",value=start,key="metric_start")
            reach=st.number_input("Reach",min_value=0,value=0)
            impressions=st.number_input("Impressions",min_value=0,value=0)
            likes=st.number_input("Likes",min_value=0,value=0)
            comments=st.number_input("Comments",min_value=0,value=0)
            shares=st.number_input("Shares",min_value=0,value=0)
        with m2:
            pe=st.date_input("Metric period end",value=end,key="metric_end")
            clicks=st.number_input("Clicks",min_value=0,value=0)
            leads=st.number_input("Leads",min_value=0,value=0)
            spend=st.number_input("Spend",min_value=0.0,value=0.0)
            source=st.selectbox("Data source",["Manually entered","Platform export","Sample data"])
            notes=st.text_input("Notes")
        add=st.form_submit_button("Save metrics")
    if add:
        if metric_client is None: st.error("Create/select a client first.")
        elif pe < ps: st.error("Period end must be on or after period start.")
        else:
            try:
                reporting_service.add_metric({"client_id":metric_client,"platform":metric_platform,
                    "period_start":ps,"period_end":pe,"reach":reach,"impressions":impressions,
                    "likes":likes,"comments":comments,"shares":shares,"clicks":clicks,"leads":leads,
                    "spend":spend,"source_label":source,"notes":notes})
                st.success("Metrics saved."); st.rerun()
            except Exception as e: safe_error("Could not save metrics",e)
    st.subheader("Create report")
    title=st.text_input("Report title",value="Marketing performance report")
    if st.button("Generate report from saved metrics",type="primary"):
        if cid is None: st.error("Select a client for the report.")
        else:
            try:
                report_id, report=reporting_service.create_report(cid,title,start,end)
                st.success(f"Report #{report_id} saved.")
                st.markdown(report)
                st.download_button("Download report (.md)",report,file_name=f"marketing_report_{report_id}.md")
            except Exception as e: safe_error("Could not create report",e)
    reports=reporting_service.list_reports(cid)
    if reports:
        with st.expander("Saved reports"):
            for rep in reports:
                st.markdown(f"**{rep['title']}** · {rep['created_at']}")
                st.download_button(f"Download #{rep['id']}",rep["report_text"],file_name=f"report_{rep['id']}.md",key=f"report_dl_{rep['id']}")

def render_settings():
    st.title("Settings")
    st.caption("Local model configuration and demonstration data.")
    cfg=ollama_settings(); status=connection_status()
    a,b,c=st.columns(3)
    a.metric("Ollama connection","Connected" if status["connected"] else "Offline")
    b.metric("Configured model",cfg["model"])
    c.metric("Model available","Yes" if status["model_found"] else "No")
    if status["connected"] and status["model_found"]: st.success(status["message"])
    else: st.warning(status["message"])
    st.markdown("**Configuration values**")
    st.code(f"OLLAMA_BASE_URL={cfg['base_url']}\nOLLAMA_MODEL={cfg['model']}\nOLLAMA_TIMEOUT_SECONDS={cfg['timeout']}")
    st.markdown("Change these in `.env`, then restart Streamlit.")
    if st.button("Recheck Ollama connection"): st.rerun()
    if status["models"]:
        st.write("Models reported by local Ollama:",status["models"])
    st.markdown("#### Install Ollama and the recommended model")
    st.code("ollama pull qwen3:4b\n# then start the app in another terminal",language="bash")
    st.markdown("See README for full setup instructions.")
    st.subheader("Sample clients")
    st.caption("The two sample businesses are clearly marked as demonstration data. Website/account information is not independently verified.")
    if st.button("Load sample clients",type="primary"):
        sample_path=Path(__file__).parent/"data"/"sample_clients.json"
        samples=json.loads(sample_path.read_text(encoding="utf-8"))
        existing={c["company_name"].casefold() for c in clients()}
        added=0
        for sample in samples:
            if sample["company_name"].casefold() not in existing:
                client_service.create_client(sample); added+=1
        st.success(f"Added {added} sample client(s)."); st.rerun()
    if clients() and st.button("Reset demo data"):
        st.warning("Reset demo data is not enabled because this beta cannot reliably distinguish sample records from real client records. Delete sample clients individually from Clients.")

PAGES = {
 "Dashboard":render_dashboard,
 "Clients":render_clients,
 "Digital Presence Audit":render_presence,
 "Marketing Strategy":render_strategy,
 "AI Content Studio":render_content_studio,
 "Content Calendar":render_calendar,
 "Approvals":render_approvals,
 "Analytics and Reports":render_reports,
 "Settings":render_settings,
}
with st.sidebar:
    st.markdown("## 📈 Marketing Ops")
    st.caption("Agency workspace")
    selected=st.radio("Navigation",list(PAGES),label_visibility="collapsed")
    st.divider()
    stat=connection_status()
    st.caption("LOCAL AI")
    st.markdown(("🟢 Ready" if stat["connected"] and stat["model_found"] else "🟠 Setup required"))
    st.caption(f"Model: {stat['model']}")
    st.divider()
    st.caption("Beta · Local SQLite · Human approval required")
PAGES[selected]()
