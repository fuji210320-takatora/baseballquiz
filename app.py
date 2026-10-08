import streamlit as st
ページ設定
st.set_page_config(page_title="成績クイズ", page_icon="⚾", layout="centered")
カスタムCSSの注入
st.markdown("""
""", unsafe_allow_html=True)
====== ヘッダー部分 ======
st.markdown("成績クイズ", unsafe_allow_html=True)
st.markdown("知識をクイズで鍛えよう", unsafe_allow_html=True)
st.markdown("ランキングを見る", unsafe_allow_html=True)
====== セッションステート（状態管理）の初期化 ======
どのボタンが選択されているかを保持します
if 'position' not in st.session_state: st.session_state.position = '野手'
if 'league' not in st.session_state: st.session_state.league = '全て'
if 'q_count' not in st.session_state: st.session_state.q_count = '3問'
====== UI構築 ======
カード風のUIをまとめるためのコンテナ
with st.container():
# --- 出題範囲（ポジション） ---
st.markdown("<div class='section-label'>出題範囲 (ポジション)</div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
positions = ["投手", "野手", "全て"]
for i, opt in enumerate(positions):
    # 選択中なら primary(ネイビー), 未選択なら secondary(白) にする
    btn_type = "primary" if st.session_state.position == opt else "secondary"
    if [c1, c2, c3][i].button(opt, key=f"pos_{opt}", use_container_width=True, type=btn_type):
        st.session_state.position = opt
        st.rerun()

# --- 出題範囲（リーグ） ---
st.markdown("<div class='section-label'>出題範囲 (リーグ)</div>", unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)
leagues = ["セ・リーグ", "パ・リーグ", "全て"]
for i, opt in enumerate(leagues):
    btn_type = "primary" if st.session_state.league == opt else "secondary"
    if [c4, c5, c6][i].button(opt, key=f"leg_{opt}", use_container_width=True, type=btn_type):
        st.session_state.league = opt
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True) # 少し余白

# --- フィルター（アコーディオン） ---
with st.expander("フィルター"):
    st.number_input("最低打席数の制限", min_value=0, value=100, step=10)
    st.number_input("最低投球回数の制限", min_value=0, value=50, step=10)

# --- 出題数（2x2グリッド配置） ---
st.markdown("<div class='section-label'>出題数</div>", unsafe_allow_html=True)

# 上の段 (3問 / 5問)
q1, q2 = st.columns(2)
if q1.button("3問", key="q_3", use_container_width=True, type="primary" if st.session_state.q_count == "3問" else "secondary"):
    st.session_state.q_count = "3問"
    st.rerun()
if q2.button("5問", key="q_5", use_container_width=True, type="primary" if st.session_state.q_count == "5問" else "secondary"):
    st.session_state.q_count = "5問"
    st.rerun()

# 下の段 (10問 / エンドレス)
q3, q4 = st.columns(2)
if q3.button("10問", key="q_10", use_container_width=True, type="primary" if st.session_state.q_count == "10問" else "secondary"):
    st.session_state.q_count = "10問"
    st.rerun()
if q4.button("エンドレス", key="q_end", use_container_width=True, type="primary" if st.session_state.q_count == "エンドレス" else "secondary"):
    st.session_state.q_count = "エンドレス"
    st.rerun()

# --- 出題対象テキスト ---
# ※実際のアプリではフィルタやリーグ選択に応じてここの数字を動的に計算します
st.markdown("<div class='target-count'>出題対象: 322人</div>", unsafe_allow_html=True)

# --- クイズ開始ボタン ---
# （CSSでこのボタンだけ緑色の大型ボタンになるよう設定しています）
if st.button("クイズ開始", type="primary", use_container_width=True):
    st.toast(f"{st.session_state.position} / {st.session_state.league} / {st.session_state.q_count} でクイズを開始します！")


====== フッター部分（説明文） ======
st.markdown("""
