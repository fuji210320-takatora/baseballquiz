import streamlit as st
import pandas as pd
import random

# ===== 1. データの準備（ダミーデータ） =====
@st.cache_data
def load_data():
    # ※実際にご自身のエクセルを使う場合は以下のように変更してください
    # return pd.read_excel("baseball_data.xlsx", sheet_name=None)
    
    batters = pd.DataFrame({
        "選手名": ["近本光司", "大山悠輔", "牧秀悟", "村上宗隆", "柳田悠岐", "万波中正"],
        "球団": ["阪神", "阪神", "DeNA", "ヤクルト", "ソフトバンク", "日本ハム"],
        "ポジション": ["外野手", "一塁手", "二塁手", "三塁手", "外野手", "外野手"],
        "投打": ["左投左打", "右投右打", "右投右打", "右投左打", "右投左打", "右投右打"],
        "試合数": [143, 143, 143, 143, 119, 141],
        "打席数": [600, 580, 605, 595, 480, 550], # フィルター用
        "打率": [".285", ".288", ".293", ".256", ".299", ".265"],
        "本塁打": [8, 19, 29, 31, 22, 25],
        "打点": [54, 78, 103, 84, 85, 74],
        "盗塁": [28, 3, 2, 4, 1, 0],
        "OPS": [".749", ".843", ".867", ".875", ".901", ".789"]
    })
    pitchers = pd.DataFrame({
        "選手名": ["村上頌樹", "東克樹", "戸郷翔征", "山本由伸", "佐々木朗希", "平良海馬"],
        "球団": ["阪神", "DeNA", "巨人", "オリックス", "ロッテ", "西武"],
        "ポジション": ["先発", "先発", "先発", "先発", "先発", "先発"],
        "投打": ["右投左打", "左投左打", "右投右打", "右投右打", "右投右打", "右投右打"],
        "登板数": [22, 24, 24, 23, 15, 23],
        "投球回": [144.1, 172.1, 170.0, 164.0, 91.0, 150.0], # フィルター用
        "防御率": ["1.75", "1.98", "2.38", "1.21", "1.78", "2.40"],
        "勝利": [10, 16, 12, 16, 7, 11],
        "奪三振": [137, 133, 141, 169, 135, 153],
        "勝率": [".667", ".842", ".706", ".727", ".636", ".579"],
        "WHIP": ["0.74", "0.96", "1.05", "0.88", "0.75", "1.13"]
    })
    return {"野手": batters, "投手": pitchers}

dfs = load_data()

# ===== 2. 状態管理（Session State） =====
if 'current_page' not in st.session_state: st.session_state.current_page = 'start'
if 'quiz_pool' not in st.session_state: st.session_state.quiz_pool = []
if 'q_index' not in st.session_state: st.session_state.q_index = 0
if 'score' not in st.session_state: st.session_state.score = 0

# 各問題のヒントや解答状態
def reset_question_state():
    st.session_state.hint_bat = False
    st.session_state.hint_pos = False
    st.session_state.hint_team = False
    st.session_state.is_answered = False
    st.session_state.is_correct = False

if 'is_answered' not in st.session_state: reset_question_state()

# ===== 3. 共通CSS =====
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
button[kind="primary"]:hover { background-color: #0f766e !important; }
</style>
""", unsafe_allow_html=True)


# ===== 4. スタート画面 =====
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
        q_count_str = st.pills(
            "出題数",
            options=["3問", "5問", "10問", "エンドレス"],
            selection_mode="single",
            default="3問",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # クイズ開始ボタンとデータ絞り込み処理
        if st.button("クイズ開始", type="primary", use_container_width=True):
            # 球団のリスト（フィルター用）
            central = ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日"]
            pacific = ["オリックス", "ロッテ", "ソフトバンク", "楽天", "西武", "日本ハム"]
            
            scopes = selected_scopes if selected_scopes else []
            is_all = "全て" in scopes or len(scopes) == 0
            
            # リーグの絞り込み
            allowed_leagues = []
            if is_all or ("セ" not in scopes and "パ" not in scopes):
                allowed_leagues = central + pacific
            else:
                if "セ" in scopes: allowed_leagues.extend(central)
                if "パ" in scopes: allowed_leagues.extend(pacific)
            
            # 投打の絞り込み
            allowed_roles = []
            if is_all or ("野手" not in scopes and "投手" not in scopes):
                allowed_roles = ["野手", "投手"]
            else:
                if "野手" in scopes: allowed_roles.append("野手")
                if "投手" in scopes: allowed_roles.append("投手")

            # 条件に合う選手を抽出
            pool = []
            if "野手" in allowed_roles:
                b_df = dfs["野手"]
                filtered_b = b_df[(b_df["球団"].isin(allowed_leagues)) & (b_df["打席数"] >= min_pa)]
                for _, row in filtered_b.iterrows():
                    d = row.to_dict()
                    d['type'] = '野手'
                    pool.append(d)
                    
            if "投手" in allowed_roles:
                p_df = dfs["投手"]
                filtered_p = p_df[(p_df["球団"].isin(allowed_leagues)) & (p_df["投球回"] >= min_ip)]
                for _, row in filtered_p.iterrows():
                    d = row.to_dict()
                    d['type'] = '投手'
                    pool.append(d)

            # エラー処理 または クイズ開始処理
            if len(pool) == 0:
                st.error("条件に合う選手がいません！フィルターを緩めてください。")
            else:
                random.shuffle(pool) # 問題をシャッフル
                # 問題数を決定
                if q_count_str == "エンドレス":
                    max_q = len(pool)
                else:
                    max_q = min(int(q_count_str.replace("問", "")), len(pool))
                
                st.session_state.quiz_pool = pool[:max_q]
                st.session_state.score = 0
                st.session_state.q_index = 0
                reset_question_state()
                st.session_state.current_page = 'quiz'
                st.rerun()

    st.markdown("""
    <div style='background-color: #f9fafb; padding: 20px; border-radius: 8px; color: #4b5563; font-size: 14px; margin-top: 20px;'>
    成績クイズは、表示された成績の数字から選手名を当てるクイズです。打席数や投球回数のフィルターを活用して難易度を調整できます。
    </div>
    """, unsafe_allow_html=True)


# ===== 5. クイズ画面 =====
def show_quiz_page():
    # 上部メニュー
    if st.button("← 中断してスタート画面に戻る"):
        st.session_state.current_page = 'start'
        st.rerun()
        
    total_q = len(st.session_state.quiz_pool)
    current_idx = st.session_state.q_index
    player = st.session_state.quiz_pool[current_idx]
    
    st.markdown(f"<h4 style='text-align: center; color: #6b7280;'>第 {current_idx + 1} 問 / {total_q}問中</h4>", unsafe_allow_html=True)
    st.markdown("<h2 class='title-text' style='font-size: 24px; margin-bottom: 20px;'>⚾ この成績の選手は誰？</h2>", unsafe_allow_html=True)

    # 成績表示 (野手と投手で表示を切り替え)
    with st.container(border=True):
        if player['type'] == '野手':
            c1, c2, c3 = st.columns(3)
            c1.metric("打率", player['打率'])
            c2.metric("本塁打", f"{player['本塁打']}本")
            c3.metric("打点", f"{player['打点']}")
            c4, c5, c6 = st.columns(3)
            c4.metric("盗塁", f"{player['盗塁']}")
            c5.metric("OPS", player['OPS'])
            c6.metric("試合数", f"{player['試合数']}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("防御率", player['防御率'])
            c2.metric("勝利", f"{player['勝利']}勝")
            c3.metric("奪三振", f"{player['奪三振']}")
            c4, c5, c6 = st.columns(3)
            c4.metric("勝率", player['勝率'])
            c5.metric("WHIP", player['WHIP'])
            c6.metric("登板数", f"{player['登板数']}")

    # ヒントセクション
    st.markdown("#### 💡 ヒント")
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        if st.button("投打を見る", use_container_width=True): st.session_state.hint_bat = True
    with h_col2:
        if st.button("ポジション", use_container_width=True): st.session_state.hint_pos = True
    with h_col3:
        if st.button("所属球団", use_container_width=True): st.session_state.hint_team = True

    hints = []
    if st.session_state.hint_bat: hints.append(f"投打: {player['投打']}")
    if st.session_state.hint_pos: hints.append(f"ポジション: {player['ポジション']}")
    if st.session_state.hint_team: hints.append(f"球団: {player['球団']}")
    if hints:
        st.info(" ／ ".join(hints))

    st.markdown("---")

    # 解答入力と判定
    answer_input = st.text_input("選手名を入力 (フルネーム)", placeholder="例: 近本光司", disabled=st.session_state.is_answered)
    
    if not st.session_state.is_answered:
        ans_col, skip_col = st.columns(2)
        with ans_col:
            if st.button("解答する", type="primary", use_container_width=True):
                # 空白を取り除いて判定（大山 悠輔などスペース入りに対応）
                clean_input = answer_input.replace(" ", "").replace(" ", "")
                if clean_input == player['選手名']:
                    st.session_state.is_correct = True
                    st.session_state.score += 1
                st.session_state.is_answered = True
                st.rerun()
        with skip_col:
            if st.button("分からない", use_container_width=True):
                st.session_state.is_correct = False
                st.session_state.is_answered = True
                st.rerun()
    else:
        # 結果表示と次へ進むボタン
        if st.session_state.is_correct:
            st.success(f"🎉 大正解！ 答えは「{player['選手名']}」でした！")
        else:
            st.error(f"残念！ 正解は「{player['選手名']}」でした。")
            
        if current_idx + 1 < total_q:
            if st.button("次の問題へ ➡", type="primary", use_container_width=True):
                st.session_state.q_index += 1
                reset_question_state()
                st.rerun()
        else:
            if st.button("結果を見る 🏆", type="primary", use_container_width=True):
                st.session_state.current_page = 'result'
                st.rerun()


# ===== 6. 結果画面 =====
def show_result_page():
    st.markdown("<h1 class='title-text'>クイズ終了！</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_q = len(st.session_state.quiz_pool)
    score = st.session_state.score
    
    st.markdown(f"<h2 style='text-align: center;'>{total_q}問中 <span style='color: #0d9488; font-size: 48px;'>{score}</span> 問正解！</h2>", unsafe_allow_html=True)
    st.balloons() # クリア演出の風船！
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("トップへ戻る", type="primary", use_container_width=True):
        st.session_state.current_page = 'start'
        st.rerun()

# ===== 7. 画面のルーティング =====
if st.session_state.current_page == 'start':
    show_start_page()
elif st.session_state.current_page == 'quiz':
    show_quiz_page()
elif st.session_state.current_page == 'result':
    show_result_page()
