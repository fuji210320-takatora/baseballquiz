import streamlit as st

# セッションステート（状態管理）の初期化
if 'scope' not in st.session_state:
    st.session_state.scope = "全て"
if 'q_count' not in st.session_state:
    st.session_state.q_count = "3問"

# --- 画面UIデザインの適用 ---
st.markdown("""
<style>
/* 全体的なフォントや余白の調整 */
.title-text { text-align: center; color: #1f2937; margin-bottom: 0px; font-weight: 800; }
.sub-text { text-align: center; color: #6b7280; font-size: 14px; }
.link-text { text-align: center; color: #0d9488; font-size: 14px; cursor: pointer; margin-bottom: 20px; }
.section-title { color: #6b7280; font-size: 14px; margin-bottom: 10px; font-weight: bold; }
.note-text { color: #9ca3af; font-size: 12px; margin-top: 5px; margin-bottom: 15px;}

/* クイズ開始ボタンをエメラルドグリーンにするCSSハック（画面内で最後のボタンをターゲット） */
div.stButton:last-of-type button {
    background-color: #0d9488;
    color: white;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    border: none;
    border-radius: 8px;
}
div.stButton:last-of-type button:hover {
    background-color: #0f766e;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- ヘッダー ---
st.markdown("<h1 class='title-text'>成績クイズ</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>知識をクイズで鍛えよう</p>", unsafe_allow_html=True)
st.markdown("<p class='link-text'>ランキングを見る</p>", unsafe_allow_html=True)

# --- メインコンテンツ（枠線付きコンテナ） ---
with st.container(border=True):
    st.markdown("<div class='section-title'>出題範囲</div>", unsafe_allow_html=True)
    
    # 出題範囲のボタン選択 (5列並び)
    scopes = ["投手", "野手", "セ", "パ", "全て"]
    sc_cols = st.columns(len(scopes))
    
    for col, scope_name in zip(sc_cols, scopes):
        with col:
            # 選ばれているものは青色（primary）、それ以外は灰色（secondary）になる
            b_type = "primary" if st.session_state.scope == scope_name else "secondary"
            if st.button(scope_name, type=b_type, use_container_width=True):
                st.session_state.scope = scope_name
                st.rerun()
                
    st.markdown("<div class='note-text'>※選択したレギュレーションの対象選手で絞り込みます</div>", unsafe_allow_html=True)

    # フィルター（開閉式エキスパンダー）
    with st.expander("フィルター", expanded=False):
        st.number_input("最低打席数の制限", min_value=0, value=0, step=50, help="例: 規定打席443など")
        st.number_input("最低投球回数の制限", min_value=0, value=0, step=10, help="例: 規定投球回143など")

    st.divider()

    # 出題数
    st.markdown("<div class='section-title'>出題数</div>", unsafe_allow_html=True)
    
    # 2列×2行でボタンを配置
    q_rows = [
        ("3問", "5問"),
        ("10問", "エンドレス")
    ]
    
    for r_left, r_right in q_rows:
        col_l, col_r = st.columns(2)
        with col_l:
            b_type_l = "primary" if st.session_state.q_count == r_left else "secondary"
            if st.button(r_left, type=b_type_l, use_container_width=True):
                st.session_state.q_count = r_left
                st.rerun()
        with col_r:
            b_type_r = "primary" if st.session_state.q_count == r_right else "secondary"
            if st.button(r_right, type=b_type_r, use_container_width=True):
                st.session_state.q_count = r_right
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 出題対象数の表示（※後で実際のデータ件数と連動させます）
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 20px;'>出題対象: 900人</p>", unsafe_allow_html=True)
    
    # クイズ開始ボタン
    if st.button("クイズ開始", use_container_width=True):
        # ここに本番のクイズ画面へ切り替える処理を書きます
        st.success(f"{st.session_state.scope}対象・{st.session_state.q_count}でクイズを開始します！（準備中）")

# 画面下部の説明テキスト
st.markdown("""
<div style='background-color: #f9fafb; padding: 20px; border-radius: 8px; color: #4b5563; font-size: 14px; margin-top: 20px;'>
成績クイズは、表示された成績の数字から選手名を当てるクイズです。打席数や投球回数のフィルターを活用して難易度を調整できます。
</div>
""", unsafe_allow_html=True)
