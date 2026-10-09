import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import re
import unicodedata


# =========================================================
# 名前正規化（データ読み込み時に使うため一番上に移動）
# =========================================================

def normalize_name(text):
    if pd.isna(text) or text is None:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", "", text)
    return text.strip()


# =========================================================
# データ読み込み
# =========================================================

@st.cache_data
def load_data():

    file_name = "baseball_data.xlsx"

    try:
        dfs = pd.read_excel(
            file_name,
            sheet_name=None
        )

    except FileNotFoundError:
        st.error(
            f"🚨 【エラー】同じフォルダに `{file_name}` が見つかりません。"
        )
        st.stop()

    except Exception as e:
        st.error(
            f"🚨 【エラー】ファイルの読み込みに失敗しました: {e}"
        )
        st.stop()

    # =====================================================
    # シート確認
    # =====================================================

    if "野手" not in dfs or "投手" not in dfs:
        st.error(
            "🚨 【エラー】Excelファイル内に"
            "「野手」と「投手」のシートが必要です。"
        )
        st.stop()
        
    if "基本データ" not in dfs:
        st.error(
            "🚨 【エラー】Excelファイル内に"
            "「基本データ」のシートが必要です。"
        )
        st.stop()

    # =====================================================
    # 必要列
    # =====================================================

    required_batter = [
        "選手名", "球団", "試合数", "打席数", "打率", 
        "本塁打", "打点", "盗塁", "出塁率", "OPS"
    ]

    required_pitcher = [
        "選手名", "球団", "登板数", "投球回", "防御率", 
        "勝利", "敗北", "セーブ", "HP", "奪三振"
    ]
    
    # 基本データから「球団」を除外
    required_basic = [
        "選手名", "生年月日", "年数", "年俸", 
        "投打", "出身", "背番号"
    ]

    missing_b = [col for col in required_batter if col not in dfs["野手"].columns]
    missing_p = [col for col in required_pitcher if col not in dfs["投手"].columns]
    missing_basic = [col for col in required_basic if col not in dfs["基本データ"].columns]

    if missing_b:
        st.error("🚨 「野手」シートに以下の列がありません: " + ", ".join(missing_b))
        st.stop()

    if missing_p:
        st.error("🚨 「投手」シートに以下の列がありません: " + ", ".join(missing_p))
        st.stop()
        
    if missing_basic:
        st.error("🚨 「基本データ」シートに以下の列がありません: " + ", ".join(missing_basic))
        st.stop()

    # =====================================================
    # 選手名の空白削除（絶対に残さない最強の処理）
    # =====================================================
    for sheet in ["野手", "投手", "基本データ"]:
        if sheet in dfs and "選手名" in dfs[sheet].columns:
            # normalize_name関数を適用して、全角半角や特殊スペースをすべて空文字に変換
            dfs[sheet]["選手名"] = dfs[sheet]["選手名"].apply(normalize_name)

    # =====================================================
    # 基本データを成績シートにマージ（合体）する
    # =====================================================
    
    dfs["野手"] = pd.merge(dfs["野手"], dfs["基本データ"], on="選手名", how="left")
    dfs["投手"] = pd.merge(dfs["投手"], dfs["基本データ"], on="選手名", how="left")

    # =====================================================
    # 数値化
    # =====================================================

    batter_numeric = ["試合数", "打席数", "本塁打", "打点", "盗塁"]
    pitcher_numeric = ["登板数", "投球回", "勝利", "敗北", "セーブ", "HP", "奪三振"]

    for col in batter_numeric:
        dfs["野手"][col] = pd.to_numeric(dfs["野手"][col], errors="coerce").fillna(0)

    for col in pitcher_numeric:
        dfs["投手"][col] = pd.to_numeric(dfs["投手"][col], errors="coerce").fillna(0)

    # =====================================================
    # 空欄処理
    # =====================================================

    for sheet in dfs:
        dfs[sheet] = dfs[sheet].fillna("-")

    return dfs


dfs = load_data()


# =========================================================
# 全選手名
# =========================================================

def get_all_player_names():

    names = []
    for sheet_name in ["野手", "投手"]:
        if sheet_name not in dfs:
            continue
        for name in dfs[sheet_name]["選手名"]:
            name = str(name).strip()
            if name and name != "-" and name not in names:
                names.append(name)

    return sorted(names)


ALL_PLAYER_NAMES = get_all_player_names()


# =========================================================
# 表示用フォーマット
# =========================================================

def format_integer(value):
    if value is None or str(value) == "-":
        return "-"
    try:
        return str(int(float(value)))
    except Exception:
        return str(value)

def format_rate(value):
    if value is None or str(value) == "-":
        return "-"
    try:
        formatted = f"{float(value):.3f}"
        if formatted.startswith("0."):
            return formatted[1:]
        return formatted
    except Exception:
        return str(value)

def format_era(value):
    if value is None or str(value) == "-":
        return "-"
    try:
        return f"{float(value):.2f}"
    except Exception:
        return str(value)

def format_decimal(value):
    if value is None or str(value) == "-":
        return "-"
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return str(number)
    except Exception:
        return str(value)


# =========================================================
# Session State
# =========================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "start"

if "quiz_pool" not in st.session_state:
    st.session_state.quiz_pool = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "is_answered" not in st.session_state:
    st.session_state.is_answered = False

if "is_correct" not in st.session_state:
    st.session_state.is_correct = False

if "hint_limits" not in st.session_state:
    st.session_state.hint_limits = {}

if "opened_hints" not in st.session_state:
    st.session_state.opened_hints = []


def reset_question_state():
    st.session_state.is_answered = False
    st.session_state.is_correct = False
    st.session_state.opened_hints = []


# =========================================================
# 通常CSS
# =========================================================

st.markdown(
    """
    <style>
    .title-text {
        text-align: center;
        color: #1f2937;
        font-weight: 800;
        font-size: 32px;
    }
    .sub-text {
        text-align: center;
        color: #6b7280;
        font-size: 14px;
    }
    .section-title {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .note-text {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    button[kind="primary"] {
        background-color: #0d9488 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:hover {
        background-color: #0f766e !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 成績カード
# =========================================================

def show_stats_card(player):

    if player["type"] == "投手":
        stats = [
            ("登板数", f"{format_integer(player['登板数'])}試合"),
            ("投球回", format_decimal(player["投球回"])),
            ("防御率", format_era(player["防御率"])),
            ("奪三振", format_integer(player["奪三振"])),
            ("勝利", f"{format_integer(player['勝利'])}勝"),
            ("敗北", f"{format_integer(player['敗北'])}敗"),
            ("セーブ", format_integer(player["セーブ"])),
            ("HP", format_integer(player["HP"]))
        ]
        title = "投手成績"
    else:
        stats = [
            ("試合数", f"{format_integer(player['試合数'])}試合"),
            ("打率", format_rate(player["打率"])),
            ("本塁打", f"{format_integer(player['本塁打'])}本"),
            ("打点", format_integer(player["打点"])),
            ("打席数", format_integer(player["打席数"])),
            ("出塁率", format_rate(player["出塁率"])),
            ("盗塁", format_integer(player["盗塁"])),
            ("OPS", format_rate(player["OPS"]))
        ]
        title = "野手成績"

    top_html = ""
    for label, value in stats[:4]:
        top_html += f"""
        <div class="stat-item">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """

    bottom_html = ""
    for label, value in stats[4:]:
        bottom_html += f"""
        <div class="stat-item">
            <div class="stat-label">{label}</div>
            <div class="stat-value-small">{value}</div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{
                margin: 0; padding: 0; background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", sans-serif;
            }}
            .stats-card {{
                width: 100%; background: #ffffff;
                border: 2px solid #d6d3cc; border-radius: 7px;
                padding: 34px 42px 38px 42px;
            }}
            .stats-header {{
                display: flex; justify-content: space-between;
                align-items: center; margin-bottom: 28px;
            }}
            .stats-title {{
                font-size: 27px; font-weight: 800;
                color: #171717; letter-spacing: 1px;
            }}
            .stats-year {{
                font-size: 24px; color: #6b7280; font-weight: 400;
            }}
            .stats-line {{
                width: 100%; height: 3px; background: #202020; margin-bottom: 45px;
            }}
            .stats-grid-top, .stats-grid-bottom {{
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
            }}
            .stats-grid-top {{ margin-bottom: 42px; }}
            .stat-item {{ text-align: center; min-width: 0; }}
            .stat-label {{
                color: #70757a; font-size: 18px; font-weight: 700;
                margin-bottom: 12px; white-space: nowrap;
            }}
            .stat-value {{
                color: #171717; font-size: 35px; font-weight: 800;
                line-height: 1.05; white-space: nowrap;
            }}
            .stat-value-small {{
                color: #171717; font-size: 32px; font-weight: 800;
                line-height: 1.05; white-space: nowrap;
            }}
            @media (max-width: 700px) {{
                .stats-card {{ padding: 25px 10px 30px 10px; }}
                .stats-header {{ margin-bottom: 20px; }}
                .stats-title, .stat-value-small {{ font-size: 22px; }}
                .stats-year {{ font-size: 18px; }}
                .stats-line {{ height: 2px; margin-bottom: 30px; }}
                .stats-grid-top, .stats-grid-bottom {{ gap: 2px; }}
                .stats-grid-top {{ margin-bottom: 34px; }}
                .stat-label {{ font-size: 12px; margin-bottom: 9px; }}
                .stat-value {{ font-size: 23px; }}
            }}
        </style>
    </head>
    <body>
        <div class="stats-card">
            <div class="stats-header">
                <div class="stats-title">{title}</div>
                <div class="stats-year">2026年</div>
            </div>
            <div class="stats-line"></div>
            <div class="stats-grid-top">{top_html}</div>
            <div class="stats-grid-bottom">{bottom_html}</div>
        </div>
    </body>
    </html>
    """

    components.html(html, height=340, scrolling=False)


# =========================================================
# スタート画面
# =========================================================

def show_start_page():

    st.markdown("<h1 class='title-text'>成績クイズ</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>知識をクイズで鍛えよう</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):

        st.markdown("<div class='section-title'>出題範囲</div>", unsafe_allow_html=True)

        selected_scopes = st.pills(
            "出題範囲",
            options=["投手", "野手", "セ", "パ"],
            selection_mode="multi",
            default=["投手", "野手", "セ", "パ"],
            label_visibility="collapsed"
        )

        st.markdown(
            "<div class='note-text'>※選択した条件の選手から出題されます</div>",
            unsafe_allow_html=True
        )

        # -------------------------------------------------
        # フィルターUI
        # -------------------------------------------------
        with st.expander("フィルター設定", expanded=False):

            st.markdown("**【野手】**")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                min_pa = st.number_input("最低打席数", min_value=0, value=350, step=10)
            with col_b2:
                min_games_b = st.number_input("最低試合数", min_value=0, value=50, step=1)
            
            filter_op_b = st.radio(
                "野手の条件結びつき",
                ["AND（すべて満たす）", "OR（いずれかを満たす）"],
                horizontal=True, key="filter_op_b", index=1
            )

            st.divider()

            st.markdown("**【投手】**")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                min_ip = st.number_input("最低投球回数", min_value=0.0, value=80.0, step=10.0)
            with col_p2:
                min_games_p = st.number_input("最低登板数", min_value=0, value=15, step=1)
            
            filter_op_p = st.radio(
                "投手の条件結びつき",
                ["AND（すべて満たす）", "OR（いずれかを満たす）"],
                horizontal=True, key="filter_op_p", index=1
            )

        # -------------------------------------------------
        # ヒント設定UI
        # -------------------------------------------------
        with st.expander("ヒント設定", expanded=False):
            st.markdown(
                "<div class='note-text'>※1回のクイズ（全問題を通して）で使用できる上限回数を設定します</div>",
                unsafe_allow_html=True
            )
            
            hint_types = ["球団", "生年月日", "年数", "年俸", "投打", "出身", "背番号"]
            hint_config = {}
            
            # 初期設定でオンにするヒントのリスト
            default_on_hints = ["球団", "年数", "背番号"]
            
            for ht in hint_types:
                h_col1, h_col2 = st.columns([1, 1])
                with h_col1:
                    # default_on_hintsに含まれていればTrue、それ以外はFalse
                    is_on = st.checkbox(f"「{ht}」を使用", value=(ht in default_on_hints))
                with h_col2:
                    limit = st.number_input(f"{ht}上限回数", min_value=1, max_value=1000, value=1, step=1, label_visibility="collapsed")
                hint_config[ht] = {"is_on": is_on, "limit": limit}

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

            # --- ヒントの使用制限をStateに保存 ---
            active_hints = {}
            for ht, config in hint_config.items():
                if config["is_on"]:
                    active_hints[ht] = config["limit"]
            st.session_state.hint_limits = active_hints


            central = ["阪神", "広島", "DeNA", "巨人", "ヤクルト", "中日"]
            pacific = ["オリックス", "ロッテ", "ソフトバンク", "楽天", "西武", "日本ハム"]

            scopes = selected_scopes if selected_scopes else []

            # リーグの判定
            allowed_teams = []
            if "セ" in scopes:
                allowed_teams.extend(central)
            if "パ" in scopes:
                allowed_teams.extend(pacific)
            
            # 投手・野手の判定
            allowed_roles = []
            if "野手" in scopes:
                allowed_roles.append("野手")
            if "投手" in scopes:
                allowed_roles.append("投手")

            # 出題プール生成
            pool = []

            # 野手処理
            if "野手" in allowed_roles:
                b_df = dfs["野手"].copy()
                b_df["打席数"] = pd.to_numeric(b_df["打席数"], errors="coerce").fillna(0)
                b_df["試合数"] = pd.to_numeric(b_df["試合数"], errors="coerce").fillna(0)

                mask_team = b_df["球団"].isin(allowed_teams)

                conds_b = []
                if min_pa > 0:
                    conds_b.append(b_df["打席数"] >= min_pa)
                if min_games_b > 0:
                    conds_b.append(b_df["試合数"] >= min_games_b)

                if not conds_b:
                    mask_stats = pd.Series(True, index=b_df.index)
                else:
                    mask_stats = conds_b[0]
                    for cond in conds_b[1:]:
                        if "AND" in filter_op_b:
                            mask_stats = mask_stats & cond
                        else:
                            mask_stats = mask_stats | cond

                filtered_b = b_df[mask_team & mask_stats]
                for _, row in filtered_b.iterrows():
                    player = row.to_dict()
                    player["type"] = "野手"
                    pool.append(player)

            # 投手処理
            if "投手" in allowed_roles:
                p_df = dfs["投手"].copy()
                p_df["投球回"] = pd.to_numeric(p_df["投球回"], errors="coerce").fillna(0)
                p_df["登板数"] = pd.to_numeric(p_df["登板数"], errors="coerce").fillna(0)

                mask_team = p_df["球団"].isin(allowed_teams)

                conds_p = []
                if min_ip > 0:
                    conds_p.append(p_df["投球回"] >= min_ip)
                if min_games_p > 0:
                    conds_p.append(p_df["登板数"] >= min_games_p)

                if not conds_p:
                    mask_stats = pd.Series(True, index=p_df.index)
                else:
                    mask_stats = conds_p[0]
                    for cond in conds_p[1:]:
                        if "AND" in filter_op_p:
                            mask_stats = mask_stats & cond
                        else:
                            mask_stats = mask_stats | cond

                filtered_p = p_df[mask_team & mask_stats]
                for _, row in filtered_p.iterrows():
                    player = row.to_dict()
                    player["type"] = "投手"
                    pool.append(player)

            # 開始処理
            if not pool:
                st.error("条件に合う選手がいません。フィルターを緩めてください。")
            else:
                random.shuffle(pool)

                if q_count_str == "エンドレス":
                    question_count = len(pool)
                else:
                    question_count = min(int(q_count_str.replace("問", "")), len(pool))

                st.session_state.quiz_pool = pool[:question_count]
                st.session_state.q_index = 0
                st.session_state.score = 0
                reset_question_state()
                st.session_state.current_page = "quiz"
                st.rerun()


# =========================================================
# クイズ画面
# =========================================================

def show_quiz_page():

    # 中断
    if st.button("← 中断してスタート画面に戻る"):
        st.session_state.current_page = "start"
        st.rerun()

    # 選手取得
    total_q = len(st.session_state.quiz_pool)
    current_idx = st.session_state.q_index
    player = st.session_state.quiz_pool[current_idx]

    # 問題番号
    st.markdown(
        f"""
        <h4 style="text-align:center; color:#6b7280;">
            第 {current_idx + 1} 問 / {total_q}問中
        </h4>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h2 class="title-text" style="font-size:24px;">
            ⚾ この成績の選手は誰？
        </h2>
        """,
        unsafe_allow_html=True
    )

    # 成績カード
    show_stats_card(player)

    # =====================================================
    # ヒント
    # =====================================================
    st.markdown("#### 💡 ヒント")

    if not st.session_state.hint_limits:
        st.markdown("<p style='color: #6b7280; font-size: 14px;'>※使用できるヒントはありません</p>", unsafe_allow_html=True)
    else:
        # ヒントボタンを2列で配置
        hint_cols = st.columns(2)
        idx = 0
        for ht, remaining in st.session_state.hint_limits.items():
            col = hint_cols[idx % 2]
            with col:
                # 既にこの問題で開いているヒントの場合
                if ht in st.session_state.opened_hints:
                    hint_value = player.get(ht, "-")
                    
                    # --- ここで表示フォーマットの整形 ---
                    val_str = str(hint_value)
                    if ht == "背番号":
                        if val_str.endswith(".0"):
                            hint_value = val_str[:-2]
                    elif ht == "生年月日":
                        if " 00:00:00" in val_str:
                            hint_value = val_str.replace(" 00:00:00", "")
                            
                    st.info(f"**{ht}**: {hint_value}")
                else:
                    # まだ開いていない場合
                    if remaining > 0:
                        if st.button(f"{ht}を見る (残り{remaining}回)", use_container_width=True, key=f"btn_hint_{ht}_{current_idx}"):
                            st.session_state.opened_hints.append(ht)
                            st.session_state.hint_limits[ht] -= 1
                            st.rerun()
                    else:
                        st.button(f"{ht} (使い切りました)", disabled=True, use_container_width=True, key=f"btn_hint_{ht}_{current_idx}")
            idx += 1

    st.markdown("---")

    # =====================================================
    # 選手名検索
    # =====================================================
    st.markdown("#### 選手名")

    selected_player = st.selectbox(
        "選手名を検索",
        options=ALL_PLAYER_NAMES,
        index=None,
        placeholder="選手名を入力してください",
        key=f"player_search_{current_idx}",
        label_visibility="collapsed",
        disabled=st.session_state.is_answered
    )

    # =====================================================
    # 解答
    # =====================================================
    if not st.session_state.is_answered:
        answer_col, skip_col = st.columns([3, 1])
        with answer_col:
            if st.button("解答", type="primary", use_container_width=True):
                if selected_player is None:
                    st.warning("選手名を検索して選択してください。")
                else:
                    input_name = normalize_name(selected_player)
                    correct_name = normalize_name(player["選手名"])

                    if input_name == correct_name:
                        st.session_state.is_correct = True
                        st.session_state.score += 1
                    else:
                        st.session_state.is_correct = False

                    st.session_state.is_answered = True
                    st.rerun()
        with skip_col:
            if st.button("分からない", use_container_width=True):
                st.session_state.is_correct = False
                st.session_state.is_answered = True
                st.rerun()

    # =====================================================
    # 解答後
    # =====================================================
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
                st.session_state.current_page = "result"
                st.rerun()


# =========================================================
# 結果画面
# =========================================================

def show_result_page():

    st.markdown("<h1 class='title-text'>クイズ終了！</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    total_q = len(st.session_state.quiz_pool)
    score = st.session_state.score

    st.markdown(
        f"""
        <h2 style="text-align:center;">
            {total_q}問中
            <span style="color:#0d9488; font-size:48px;">
                {score}
            </span>
            問正解！
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.balloons()
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("トップへ戻る", type="primary", use_container_width=True):
        st.session_state.current_page = "start"
        st.rerun()


# =========================================================
# 画面ルーティング
# =========================================================

if st.session_state.current_page == "start":
    show_start_page()
elif st.session_state.current_page == "quiz":
    show_quiz_page()
elif st.session_state.current_page == "result":
    show_result_page()
