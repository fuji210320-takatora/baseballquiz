import streamlit as st
import pandas as pd

# ===== 1. 状態管理（画面の切り替え用） =====
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'start' # 初期画面は 'start'

# クイズ設定の保存用
if 'settings' not in st.session_state:
    st.session_state.settings = {}

# ===== 2. 共通のCSS =====
st.markdown("""
<style>
.title-text { text-align: center; color: #1f2937; margin-bottom: 0px; font-weight: 800; font-size: 32px; }
.sub-text { text-align: center; color: #6b7280; font-size: 14px; }
.link-text { text-align: center; color: #0d9488; font-size: 14px; cursor: pointer; margin-bottom: 20px; }
.section-title { color: #6b7280; font-size: 14px; margin-bottom: 10px; font-weight: bold; }
.note-text { color: #9ca3af; font-size: 12px; margin-top: 5px; margin-bottom: 15px;}

button[kind="primary"] {
    background-color: #0d9488 !important;
    color: white !important;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    border: none !important;
    border-radius: 8px;
}
button[kind="primary"]:hover {
    background-color: #0f766e !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 3. スタート画面の関数 =====
def show_start_page():
    st.markdown("<h1 class='title-text'>成績クイズ</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>知識をクイズで鍛えよう</p>", unsafe_allow_html=True)
    st.markdown("<p class='link-text'>ランキングを見る</p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='section-title'>出題範囲</div>", unsafe_allow_html=True)
        
        selected_scopes = st.pills(
            "出題範囲",
            options=["投手", "野手", "セ", "パ", "全て"],
            selection_mode="multi",
            default=["全て"],
            label_visibility="collapsed"
        )
        st.markdown("<div class='note-text'>※選択したレギュレーションの対象選手で絞り込みます</div>", unsafe_allow_html=True)

        with st.expander("フィルター", expanded=False):
            min_pa = st.number_input("最低打席数の制限", min_value=0, value=0, step=50)
            min_ip = st.number_input("最低投球回数の制限", min_value=0, value=0, step=10)

        st.divider()

        st.markdown("<div class='section-title'>出題数</div>", unsafe_allow_html=True)
        q_count = st.pills(
            "出題数",
            options=["3問", "5問", "10問", "エンドレス"],
            selection_mode="single",
            default="3問",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 20px;'>出題対象: 900人</p>", unsafe_allow_html=True)
        
        # ★ここがポイント！ボタンを押したら画面状態を 'quiz' に切り替える
        if st.button("クイズ開始", type="primary", use_container_width=True):
            st.session_state.settings = {
                "scopes": selected_scopes,
                "q_count": q_count,
                "min_pa": min_pa,
                "min_ip": min_ip
            }
            st.session_state.current_page = 'quiz' # 画面を切り替えるフラグ
            st.rerun() # 画面を再読み込みしてクイズ画面へ！

    st.markdown("""
    <div style='background-color: #f9fafb; padding: 20px; border-radius: 8px; color: #4b5563; font-size: 14px; margin-top: 20px;'>
    成績クイズは、表示された成績の数字から選手名を当てるクイズです。打席数や投球回数のフィルターを活用して難易度を調整できます。
    </div>
    """, unsafe_allow_html=True)


# ===== 4. クイズ画面の関数（仮のモックアップ） =====
def show_quiz_page():
    # 上部に「戻る」ボタンなどを配置
    if st.button("← スタート画面に戻る"):
        st.session_state.current_page = 'start'
        st.rerun()
        
    st.markdown("<h2 class='title-text' style='font-size: 24px; margin-top: 10px;'>⚾ この成績の選手は誰？</h2>", unsafe_allow_html=True)
    
    # 選択した設定の確認表示
    settings = st.session_state.settings
    scopes_str = "、".join(settings['scopes']) if settings['scopes'] else "未選択"
    st.info(f"設定確認：【範囲】{scopes_str} 【出題数】{settings['q_count']}")
    
    # ここに以前作った成績表示（st.metric）や解答入力欄が入ります
    st.write("※ここに実際のクイズ（打率 .285, 本塁打 8 などの数字と解答欄）が表示されます。")


# ===== 5. 画面の出し分け =====
# current_page の状態によって、表示する関数を切り替える
if st.session_state.current_page == 'start':
    show_start_page()
elif st.session_state.current_page == 'quiz':
    show_quiz_page()
