import streamlit as st

# --- 画面UIデザインの適用（Radioボタンをボタングループ風にする魔法のCSS） ---
st.markdown("""
<style>
/* 全体的なフォントや余白の調整 */
.title-text { text-align: center; color: #1f2937; margin-bottom: 0px; font-weight: 800; font-size: 32px; }
.sub-text { text-align: center; color: #6b7280; font-size: 14px; }
.link-text { text-align: center; color: #0d9488; font-size: 14px; cursor: pointer; margin-bottom: 20px; }
.section-title { color: #6b7280; font-size: 14px; margin-bottom: 10px; font-weight: bold; }
.note-text { color: #9ca3af; font-size: 12px; margin-top: 5px; margin-bottom: 15px;}

/* st.radio を横並びのボタングループに変換するCSS */
div[role="radiogroup"] {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
}
div[role="radiogroup"] label {
    background-color: #ffffff;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 60px;
    transition: background-color 0.2s;
}
/* デフォルトの丸いラジオボタンを非表示にする */
div[role="radiogroup"] label > div:first-child {
    display: none;
}
/* 未選択時の文字色 */
div[role="radiogroup"] label p {
    color: #4b5563;
    font-weight: 600;
    margin: 0;
}
/* 選択時のスタイル (ネイビー) */
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #1f2937 !important;
    border-color: #1f2937 !important;
}
div[role="radiogroup"] label[data-checked="true"] p {
    color: #ffffff !important;
}

/* 「クイズ開始」ボタン（Primaryボタン）のスタイルをエメラルドグリーンに */
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
    
    # ボタンの代わりに radio を使い、CSSで横並びボタン風に見せる
    scope = st.radio(
        "出題範囲",
        ["投手", "野手", "セ", "パ", "全て"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("<div class='note-text'>※選択したレギュレーションの対象選手で絞り込みます</div>", unsafe_allow_html=True)

    with st.expander("フィルター", expanded=False):
        st.number_input("最低打席数の制限", min_value=0, value=0, step=50)
        st.number_input("最低投球回数の制限", min_value=0, value=0, step=10)

    st.divider()

    st.markdown("<div class='section-title'>出題数</div>", unsafe_allow_html=True)
    
    q_count = st.radio(
        "出題数",
        ["3問", "5問", "10問", "エンドレス"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 20px;'>出題対象: 900人</p>", unsafe_allow_html=True)
    
    # クイズ開始ボタン (type="primary" を指定することで緑色のCSSが当たる)
    if st.button("クイズ開始", type="primary", use_container_width=True):
        st.success(f"「{scope}」・「{q_count}」でクイズを開始します！")

st.markdown("""
<div style='background-color: #f9fafb; padding: 20px; border-radius: 8px; color: #4b5563; font-size: 14px; margin-top: 20px;'>
成績クイズは、表示された成績の数字から選手名を当てるクイズです。打席数や投球回数のフィルターを活用して難易度を調整できます。
</div>
""", unsafe_allow_html=True)
