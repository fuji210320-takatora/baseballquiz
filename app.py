import streamlit as st

# --- 画面UIデザインの適用 ---
# st.pillsを使うので、ボタン周りのややこしいCSSは不要になりました！
# クイズ開始ボタンだけを緑色にするCSSを残しています。
st.markdown("""
<style>
.title-text { text-align: center; color: #1f2937; margin-bottom: 0px; font-weight: 800; font-size: 32px; }
.sub-text { text-align: center; color: #6b7280; font-size: 14px; }
.link-text { text-align: center; color: #0d9488; font-size: 14px; cursor: pointer; margin-bottom: 20px; }
.section-title { color: #6b7280; font-size: 14px; margin-bottom: 10px; font-weight: bold; }
.note-text { color: #9ca3af; font-size: 12px; margin-top: 5px; margin-bottom: 15px;}

/* Primaryボタン（クイズ開始）のスタイルをエメラルドグリーンに */
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

# --- ヘッダー ---
st.markdown("<h1 class='title-text'>成績クイズ</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>知識をクイズで鍛えよう</p>", unsafe_allow_html=True)
st.markdown("<p class='link-text'>ランキングを見る</p>", unsafe_allow_html=True)

# --- メインコンテンツ（枠線付きコンテナ） ---
with st.container(border=True):
    st.markdown("<div class='section-title'>出題範囲</div>", unsafe_allow_html=True)
    
    # 【修正ポイント】st.pillsの "multi" モードで複数選択を可能に！
    # これにより「セ」と「投手」の両方押しなどが可能になります。
    selected_scopes = st.pills(
        "出題範囲",
        options=["投手", "野手", "セ", "パ", "全て"],
        selection_mode="multi", # 複数選択
        default=["全て"],
        label_visibility="collapsed"
    )
    
    st.markdown("<div class='note-text'>※選択したレギュレーションの対象選手で絞り込みます</div>", unsafe_allow_html=True)

    with st.expander("フィルター", expanded=False):
        st.number_input("最低打席数の制限", min_value=0, value=0, step=50)
        st.number_input("最低投球回数の制限", min_value=0, value=0, step=10)

    st.divider()

    st.markdown("<div class='section-title'>出題数</div>", unsafe_allow_html=True)
    
    # 出題数は1つだけ選ぶので "single" モード
    q_count = st.pills(
        "出題数",
        options=["3問", "5問", "10問", "エンドレス"],
        selection_mode="single", # 単一選択
        default="3問",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 20px;'>出題対象: 900人</p>", unsafe_allow_html=True)
    
    if st.button("クイズ開始", type="primary", use_container_width=True):
        # 複数選択された結果はリストで返ってきます (例: ["セ", "投手"])
        scopes_str = "、".join(selected_scopes) if selected_scopes else "未選択"
        st.success(f"範囲:「{scopes_str}」 / 出題数:「{q_count}」で開始します！")

st.markdown("""
<div style='background-color: #f9fafb; padding: 20px; border-radius: 8px; color: #4b5563; font-size: 14px; margin-top: 20px;'>
成績クイズは、表示された成績の数字から選手名を当てるクイズです。打席数や投球回数のフィルターを活用して難易度を調整できます。
</div>
""", unsafe_allow_html=True)
