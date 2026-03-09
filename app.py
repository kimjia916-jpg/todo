import streamlit as st
from datetime import date, datetime

st.set_page_config(page_title="할일 관리", page_icon="📋", layout="centered")

# ── 스타일 ────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .block-container { max-width: 620px; padding-top: 2rem; }
    .metric-card { background: #fff; border-radius: 12px; padding: 16px 20px;
                   box-shadow: 0 1px 4px rgba(0,0,0,0.07); text-align: center; }
    .todo-item { background: #fff; border-radius: 10px; padding: 12px 16px;
                 margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    .badge-high   { background:#FDEDEC; color:#C0392B; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    .badge-medium { background:#FEF5E7; color:#D35400; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    .badge-low    { background:#EAF2FF; color:#1A5276; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    .stButton > button { border-radius: 8px; font-family: 'Noto Sans KR', sans-serif; }
</style>
""", unsafe_allow_html=True)

PRIORITY_MAP = {
    "높음": ("high", "#C0392B", "badge-high"),
    "중간": ("medium", "#D35400", "badge-medium"),
    "낮음": ("low", "#1A5276", "badge-low"),
}
BORDER_COLOR = {"높음": "#C0392B", "중간": "#D35400", "낮음": "#1A5276"}

# ── 세션 초기화 ───────────────────────────────────────────────
if "todos" not in st.session_state:
    st.session_state.todos = [
        {"id": 1, "text": "분기별 보고서 작성", "priority": "높음", "due": date(2026, 3, 12), "done": False},
        {"id": 2, "text": "팀 미팅 준비",       "priority": "중간", "due": date(2026, 3, 10), "done": False},
        {"id": 3, "text": "이메일 정리",         "priority": "낮음", "due": None,              "done": True},
    ]
if "next_id" not in st.session_state:
    st.session_state.next_id = 4

# ── 헤더 ─────────────────────────────────────────────────────
active_count = sum(1 for t in st.session_state.todos if not t["done"])
st.markdown(f"## 📋 할일 관리 &nbsp;<span style='font-size:16px;color:#718096;font-weight:400'>{active_count}개 남음</span>", unsafe_allow_html=True)
st.markdown("<div style='height:3px;width:48px;background:#2B6CB0;border-radius:2px;margin-bottom:20px'></div>", unsafe_allow_html=True)

# ── 탭 ───────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 대시보드", "📝 일정 등록"])

# ════════════════════════════════════════════════════════════
# 탭 1 · 대시보드
# ════════════════════════════════════════════════════════════
with tab1:
    todos = st.session_state.todos
    total  = len(todos)
    done   = sum(1 for t in todos if t["done"])
    active = total - done
    high   = sum(1 for t in todos if t["priority"] == "높음" and not t["done"])
    overdue = sum(1 for t in todos if not t["done"] and t["due"] and t["due"] < date.today())
    pct = int(done / total * 100) if total else 0

    # 카드
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("전체", total)
    with c2:
        st.metric("진행중", active)
    with c3:
        st.metric("완료", done)
    with c4:
        st.metric("긴급", high)

    st.markdown("---")

    # 완료율
    st.markdown(f"**완료율** &nbsp; <span style='color:#2B6CB0;font-weight:700'>{pct}%</span>", unsafe_allow_html=True)
    st.progress(pct / 100)

    # 기한 초과 경고
    if overdue:
        st.error(f"⚠️ 기한이 초과된 할일이 **{overdue}개** 있어요!")

    st.markdown("---")

    # 전체 목록 미리보기
    st.markdown("**전체 할일 목록**")
    sorted_todos = sorted(todos, key=lambda t: (t["done"], {"높음":0,"중간":1,"낮음":2}[t["priority"]]))
    for t in sorted_todos:
        color = BORDER_COLOR[t["priority"]]
        done_style = "opacity:0.5;text-decoration:line-through;" if t["done"] else ""
        due_str = f" · {t['due'].strftime('%m/%d')}" if t["due"] else ""
        overdue_warn = " ⚠️" if not t["done"] and t["due"] and t["due"] < date.today() else ""
        badge_cls = PRIORITY_MAP[t["priority"]][2]
        st.markdown(f"""
        <div class='todo-item' style='border-left:4px solid {color};{done_style}'>
            <span class='{badge_cls}'>{t['priority']}</span>
            &nbsp; {t['text']}
            <span style='color:#A0AEC0;font-size:12px'>{due_str}{overdue_warn}</span>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 탭 2 · 일정 등록
# ════════════════════════════════════════════════════════════
with tab2:

    # ── 등록 폼 ──────────────────────────────────────────────
    with st.form("add_form", clear_on_submit=True):
        st.markdown("#### 새 일정 추가")
        text = st.text_input("할일 내용", placeholder="할일을 입력하세요...")
        col_p, col_d = st.columns(2)
        with col_p:
            priority = st.selectbox("우선순위", ["높음", "중간", "낮음"], index=1)
        with col_d:
            due = st.date_input("마감일 (선택)", value=None)
        submitted = st.form_submit_button("+ 추가", use_container_width=True, type="primary")
        if submitted and text.strip():
            st.session_state.todos.append({
                "id": st.session_state.next_id,
                "text": text.strip(),
                "priority": priority,
                "due": due,
                "done": False,
            })
            st.session_state.next_id += 1
            st.rerun()

    st.markdown("---")

    # ── 필터 ─────────────────────────────────────────────────
    filter_opt = st.radio("보기", ["전체", "진행중", "완료"], horizontal=True)

    # ── 목록 ─────────────────────────────────────────────────
    todos = st.session_state.todos
    filtered = [t for t in todos if
                (filter_opt == "전체") or
                (filter_opt == "진행중" and not t["done"]) or
                (filter_opt == "완료" and t["done"])]
    sorted_todos = sorted(filtered, key=lambda t: (t["done"], {"높음":0,"중간":1,"낮음":2}[t["priority"]]))

    if not sorted_todos:
        st.info("할일이 없어요 🎉")

    for t in sorted_todos:
        color = BORDER_COLOR[t["priority"]]
        done_style = "opacity:0.5;text-decoration:line-through;" if t["done"] else ""
        due_str = f" · {t['due'].strftime('%m/%d')}" if t["due"] else ""
        overdue_warn = " ⚠️" if not t["done"] and t["due"] and t["due"] < date.today() else ""
        badge_cls = PRIORITY_MAP[t["priority"]][2]

        col_check, col_text, col_del = st.columns([1, 10, 1])
        with col_check:
            checked = st.checkbox("", value=t["done"], key=f"done_{t['id']}")
            if checked != t["done"]:
                t["done"] = checked
                st.rerun()
        with col_text:
            st.markdown(f"""
            <div style='border-left:4px solid {color};padding:6px 12px;border-radius:6px;background:#fff;{done_style}'>
                <span class='{badge_cls}'>{t['priority']}</span>
                &nbsp; {t['text']}
                <span style='color:#A0AEC0;font-size:12px'>{due_str}{overdue_warn}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_del:
            if st.button("×", key=f"del_{t['id']}"):
                st.session_state.todos = [x for x in st.session_state.todos if x["id"] != t["id"]]
                st.rerun()
