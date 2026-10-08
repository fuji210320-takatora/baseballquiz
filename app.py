import streamlit as st
import pandas as pd
import random

# ===== 1. データの読み込みとエラーチェック（本番用） =====
@st.cache_data
def load_data():
    file_name = "baseball_data.xlsx"
    
    # 1. ファイルの存在チェック
    try:
        dfs = pd.read_excel(file_name, sheet_name=None)
    except FileNotFoundError:
        st.error(f"🚨 【エラー】同じフォルダに `{file_name}` が見つかりません。ファイル名や保存場所を確認してください。")
        st.stop() # ここでアプリの実行を停止します
    except Exception as e:
        st.error(f"🚨 【エラー】ファイルの読み込みに失敗しました: {e}")
        st.stop()

    # 2. シート名のチェック
    if "野手" not in dfs or "投手" not in dfs:
        st.error("🚨 【エラー】Excelファイル内に「野手」と「投手」のシート（タブ）が揃っていません。シート名を完全一致させてください。")
        st.stop()

    # 3. 必要な列（カラム）のチェック
    required_batter = ["選手名", "球団", "試合数", "打席数", "打率", "本塁打", "打点", "盗塁", "OPS"]
    required_pitcher = ["選手名", "球団", "登板数", "投球回", "防御率", "勝利", "奪三振", "勝率", "WHIP"]

    missing_b = [col for col in required_batter if col not in dfs["野手"].columns]
    missing_p = [col for col in required_pitcher if col not in dfs["投手"].columns]
    
    error_msgs = []
    if missing_b:
        error_msgs.append(f"「野手」シートに以下の列が足りません: {', '.join(missing_b)}")
    if missing_p:
        error_msgs.append(f"「投手」シートに以下の列が足りません: {', '.join(missing_p)}")
        
    if error_msgs:
        for msg in error_msgs:
            st.error(f"🚨 【エラー】{msg}")
        st.info("💡 エクセルの一行目（ヘッダー）の文字が、上記の列名と完全に一致しているか（余計なスペース等がないか）確認してください。")
        st.stop()

    # 欠損値（空欄）を「-」などに置き換える安全処理
    for sheet in dfs:
        dfs[sheet] = dfs[sheet].fillna("-")

    return dfs

dfs = load_data()

# ===== 2. 状態管理（Session State） =====
if 'current_page' not in st.session_state: st.session_state.current_page = 'start'
if 'quiz_pool' not in st.session_state: st.session_state.quiz_pool = []
if 'q_index' not in st.session_state: st.session_state.q_index = 0
if 'score' not in st.session_state: st.session_state.score = 0

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
        
        if st.button("クイズ開始", type="primary", use_container_width=True):
            central = ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日"]
            pacific = ["オリックス", "ロッテ", "ソフトバンク", "楽天", "西武", "日本ハム"]
            
            scopes = selected_scopes if selected_scopes else []
            is_all = "全て" in scopes or len(scopes) == 0
            
            allowed_leagues = []
            if is_all or ("セ" not in scopes and "パ" not in scopes):
                allowed_leagues = central + pacific
            else:
                if "セ" in scopes: allowed_leagues.extend(central)
                if "パ" in scopes: allowed_leagues.extend(pacific)
            
            allowed_roles = []
            if is_all or ("野手" not in scopes and "投手" not in scopes):
                allowed_roles = ["野手", "投手"]
            else:
                if "野手" in scopes: allowed_roles.append("野手")
                if "投手" in scopes: allowed_roles.append("投手")

            pool = []
            if "野手" in allowed_roles:
                b_df = dfs["野手"]
                # --- 修正前 ---
# filtered_b = b_df[(b_df["球団"].isin(allowed_leagues)) & (b_df["打席数"] >= min_pa)]

# --- 修正後 ---
# 1. 「打席数」の中身を強制的に数値型（エラー文字は0に置換）に変換
                b_df["打席数"] = pd.to_numeric(b_df["打席数"], errors="coerce").fillna(0).astype(int)

# 2. その後で比較を行う（エラーが消えます）
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

            if len(pool) == 0:
                st.error("条件に合う選手がいません！フィルターを緩めてください。")
            else:
                random.shuffle(pool)
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
    if st.button("← 中断してスタート画面に戻る"):
        st.session_state.current_page = 'start'
        st.rerun()
        
    total_q = len(st.session_state.quiz_pool)
    current_idx = st.session_state.q_index
    player = st.session_state.quiz_pool[current_idx]
    
    st.markdown(f"<h4 style='text-align: center; color: #6b7280;'>第 {current_idx + 1} 問 / {total_q}問中</h4>", unsafe_allow_html=True)
    st.markdown("<h2 class='title-text' style='font-size: 24px; margin-bottom: 20px;'>⚾ この成績の選手は誰？</h2>", unsafe_allow_html=True)

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

    answer_input = st.text_input("選手名を入力 (フルネーム)", placeholder="例: 近本光司", disabled=st.session_state.is_answered)
    
    if not st.session_state.is_answered:
        ans_col, skip_col = st.columns(2)
        with ans_col:
            if st.button("解答する", type="primary", use_container_width=True):
                clean_input = answer_input.replace(" ", "").replace(" ", "")
                if clean_input == str(player['選手名']).replace(" ", "").replace(" ", ""):
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
    st.balloons()
    
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
