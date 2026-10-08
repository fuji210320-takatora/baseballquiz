import streamlit as st
import pandas as pd
import random
import re
import unicodedata


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

    # =====================================================
    # 必要列
    # =====================================================

    required_batter = [
        "選手名",
        "球団",
        "試合数",
        "打席数",
        "打率",
        "本塁打",
        "打点",
        "盗塁",
        "OPS"
    ]

    required_pitcher = [
        "選手名",
        "球団",
        "登板数",
        "投球回",
        "防御率",
        "勝利",
        "敗北",
        "セーブ",
        "HP",
        "奪三振"
    ]

    missing_b = [
        col
        for col in required_batter
        if col not in dfs["野手"].columns
    ]

    missing_p = [
        col
        for col in required_pitcher
        if col not in dfs["投手"].columns
    ]

    if missing_b:

        st.error(
            "🚨 「野手」シートに以下の列がありません: "
            + ", ".join(missing_b)
        )
        st.stop()

    if missing_p:

        st.error(
            "🚨 「投手」シートに以下の列がありません: "
            + ", ".join(missing_p)
        )
        st.stop()

    # =====================================================
    # 数値化
    # =====================================================

    batter_numeric = [
        "試合数",
        "打席数",
        "本塁打",
        "打点",
        "盗塁"
    ]

    pitcher_numeric = [
        "登板数",
        "投球回",
        "勝利",
        "敗北",
        "セーブ",
        "HP",
        "奪三振"
    ]

    for col in batter_numeric:

        dfs["野手"][col] = pd.to_numeric(
            dfs["野手"][col],
            errors="coerce"
        ).fillna(0)

    for col in pitcher_numeric:

        dfs["投手"][col] = pd.to_numeric(
            dfs["投手"][col],
            errors="coerce"
        ).fillna(0)

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

            if (
                name
                and name != "-"
                and name not in names
            ):
                names.append(name)

    return sorted(names)


ALL_PLAYER_NAMES = get_all_player_names()


# =========================================================
# 名前正規化
# =========================================================

def normalize_name(text):

    if text is None:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        str(text)
    )

    text = re.sub(
        r"\s+",
        "",
        text
    )

    return text.strip()


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

if "hint_team" not in st.session_state:
    st.session_state.hint_team = False

if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None


def reset_question_state():

    st.session_state.is_answered = False
    st.session_state.is_correct = False
    st.session_state.hint_team = False
    st.session_state.selected_answer = None


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================================================
       全体
       ================================================ */

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

    /* ================================================
       成績カード
       ================================================ */

    .stats-card {
        background: #ffffff;
        border: 2px solid #d6d3cc;
        border-radius: 7px;
        padding: 34px 42px 38px 42px;
        margin: 12px 0 25px 0;
        box-sizing: border-box;
    }

    .stats-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 28px;
    }

    .stats-title {
        font-size: 27px;
        font-weight: 800;
        color: #171717;
        letter-spacing: 1px;
    }

    .stats-year {
        font-size: 24px;
        color: #6b7280;
        font-weight: 400;
    }

    .stats-line {
        height: 3px;
        background: #202020;
        width: 100%;
        margin-bottom: 45px;
    }

    .stats-grid-top {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 35px;
        margin-bottom: 38px;
    }

    .stats-grid-bottom {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 25px;
    }

    .stat-item {
        text-align: center;
        min-width: 0;
    }

    .stat-label {
        color: #70757a;
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 12px;
        white-space: nowrap;
    }

    .stat-value {
        color: #171717;
        font-size: 42px;
        font-weight: 800;
        line-height: 1.05;
        white-space: nowrap;
    }

    .stat-value-small {
        color: #171717;
        font-size: 37px;
        font-weight: 800;
        line-height: 1.05;
        white-space: nowrap;
    }

    /* ================================================
       スマホ
       ================================================ */

    @media (max-width: 700px) {

        .stats-card {
            padding: 25px 17px 30px 17px;
        }

        .stats-title {
            font-size: 22px;
        }

        .stats-year {
            font-size: 19px;
        }

        .stats-line {
            margin-bottom: 32px;
        }

        .stats-grid-top {
            gap: 8px;
            margin-bottom: 32px;
        }

        .stats-grid-bottom {
            gap: 7px;
        }

        .stat-label {
            font-size: 14px;
            margin-bottom: 9px;
        }

        .stat-value {
            font-size: 28px;
        }

        .stat-value-small {
            font-size: 25px;
        }
    }

    /* ================================================
       ボタン
       ================================================ */

    button[kind="primary"] {
        background-color: #0d9488 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }

    button[kind="primary"]:hover {
        background-color: #0f766e !important;
    }

    /* ================================================
       検索欄
       ================================================ */

    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 表示用関数
# =========================================================

def display_value(value):

    if value is None:
        return "-"

    if str(value) == "-":
        return "-"

    return str(value)


# =========================================================
# 成績カード
# =========================================================

def show_stats_card(player):

    if player["type"] == "投手":

        # ---------------------------------------------
        # 投手成績
        # 成績自体は7項目のまま
        #
        # 1段目
        # 登板数 / 防御率 / 勝利
        #
        # 2段目
        # 敗北 / セーブ / HP / 奪三振
        # ---------------------------------------------

        top_stats = [
            (
                "登板数",
                f"{display_value(player['登板数'])}試合"
            ),
            (
                "防御率",
                display_value(player["防御率"])
            ),
            (
                "勝利",
                f"{display_value(player['勝利'])}勝"
            )
        ]

        bottom_stats = [
            (
                "敗北",
                f"{display_value(player['敗北'])}敗"
            ),
            (
                "セーブ",
                display_value(player["セーブ"])
            ),
            (
                "HP",
                display_value(player["HP"])
            ),
            (
                "奪三振",
                display_value(player["奪三振"])
            )
        ]

        title = "投手成績"

    else:

        # ---------------------------------------------
        # 野手成績
        #
        # 1段目
        # 試合数 / 打席数 / 打率
        #
        # 2段目
        # 本塁打 / 打点 / 盗塁 / OPS
        # ---------------------------------------------

        top_stats = [
            (
                "試合数",
                f"{display_value(player['試合数'])}試合"
            ),
            (
                "打席数",
                display_value(player["打席数"])
            ),
            (
                "打率",
                display_value(player["打率"])
            )
        ]

        bottom_stats = [
            (
                "本塁打",
                f"{display_value(player['本塁打'])}本"
            ),
            (
                "打点",
                display_value(player["打点"])
            ),
            (
                "盗塁",
                display_value(player["盗塁"])
            ),
            (
                "OPS",
                display_value(player["OPS"])
            )
        ]

        title = "野手成績"

    # =====================================================
    # HTML作成
    # =====================================================

    top_html = ""

    for label, value in top_stats:

        top_html += f"""
        <div class="stat-item">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """

    bottom_html = ""

    for label, value in bottom_stats:

        bottom_html += f"""
        <div class="stat-item">
            <div class="stat-label">{label}</div>
            <div class="stat-value-small">{value}</div>
        </div>
        """

    html = f"""
    <div class="stats-card">

        <div class="stats-header">

            <div class="stats-title">
                {title}
            </div>

            <div class="stats-year">
                2026年
            </div>

        </div>

        <div class="stats-line"></div>

        <div class="stats-grid-top">
            {top_html}
        </div>

        <div class="stats-grid-bottom">
            {bottom_html}
        </div>

    </div>
    """

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# スタート画面
# =========================================================

def show_start_page():

    st.markdown(
        "<h1 class='title-text'>成績クイズ</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='sub-text'>知識をクイズで鍛えよう</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):

        st.markdown(
            "<div class='section-title'>出題範囲</div>",
            unsafe_allow_html=True
        )

        selected_scopes = st.pills(
            "出題範囲",
            options=[
                "投手",
                "野手",
                "セ",
                "パ",
                "全て"
            ],
            selection_mode="multi",
            default=["全て"],
            label_visibility="collapsed"
        )

        st.markdown(
            "<div class='note-text'>"
            "※選択した条件の選手から出題されます"
            "</div>",
            unsafe_allow_html=True
        )

        with st.expander(
            "フィルター",
            expanded=False
        ):

            min_pa = st.number_input(
                "最低打席数",
                min_value=0,
                value=0,
                step=50
            )

            min_ip = st.number_input(
                "最低投球回数",
                min_value=0.0,
                value=0.0,
                step=10.0
            )

        st.divider()

        st.markdown(
            "<div class='section-title'>出題数</div>",
            unsafe_allow_html=True
        )

        q_count_str = st.pills(
            "出題数",
            options=[
                "3問",
                "5問",
                "10問",
                "エンドレス"
            ],
            selection_mode="single",
            default="3問",
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "クイズ開始",
            type="primary",
            use_container_width=True
        ):

            central = [
                "阪神",
                "広島",
                "DeNA",
                "巨人",
                "ヤクルト",
                "中日"
            ]

            pacific = [
                "オリックス",
                "ロッテ",
                "ソフトバンク",
                "楽天",
                "西武",
                "日本ハム"
            ]

            scopes = (
                selected_scopes
                if selected_scopes
                else []
            )

            # -----------------------------------------
            # リーグ
            # -----------------------------------------

            if (
                "全て" in scopes
                or len(scopes) == 0
            ):

                allowed_teams = (
                    central + pacific
                )

            else:

                allowed_teams = []

                if "セ" in scopes:
                    allowed_teams.extend(
                        central
                    )

                if "パ" in scopes:
                    allowed_teams.extend(
                        pacific
                    )

                if not allowed_teams:

                    allowed_teams = (
                        central + pacific
                    )

            # -----------------------------------------
            # 投手・野手
            # -----------------------------------------

            if (
                "全て" in scopes
                or len(scopes) == 0
            ):

                allowed_roles = [
                    "野手",
                    "投手"
                ]

            else:

                allowed_roles = []

                if "野手" in scopes:
                    allowed_roles.append(
                        "野手"
                    )

                if "投手" in scopes:
                    allowed_roles.append(
                        "投手"
                    )

                if not allowed_roles:

                    allowed_roles = [
                        "野手",
                        "投手"
                    ]

            # -----------------------------------------
            # プール作成
            # -----------------------------------------

            pool = []

            # 野手
            if "野手" in allowed_roles:

                b_df = dfs["野手"].copy()

                b_df["打席数"] = pd.to_numeric(
                    b_df["打席数"],
                    errors="coerce"
                ).fillna(0)

                filtered_b = b_df[
                    (
                        b_df["球団"].isin(
                            allowed_teams
                        )
                    )
                    &
                    (
                        b_df["打席数"] >= min_pa
                    )
                ]

                for _, row in filtered_b.iterrows():

                    player = row.to_dict()
                    player["type"] = "野手"

                    pool.append(player)

            # 投手
            if "投手" in allowed_roles:

                p_df = dfs["投手"].copy()

                p_df["投球回"] = pd.to_numeric(
                    p_df["投球回"],
                    errors="coerce"
                ).fillna(0)

                filtered_p = p_df[
                    (
                        p_df["球団"].isin(
                            allowed_teams
                        )
                    )
                    &
                    (
                        p_df["投球回"] >= min_ip
                    )
                ]

                for _, row in filtered_p.iterrows():

                    player = row.to_dict()
                    player["type"] = "投手"

                    pool.append(player)

            # -----------------------------------------
            # 選手なし
            # -----------------------------------------

            if not pool:

                st.error(
                    "条件に合う選手がいません。"
                    "フィルターを緩めてください。"
                )

            else:

                random.shuffle(pool)

                if q_count_str == "エンドレス":

                    question_count = len(pool)

                else:

                    question_count = min(
                        int(
                            q_count_str.replace(
                                "問",
                                ""
                            )
                        ),
                        len(pool)
                    )

                st.session_state.quiz_pool = (
                    pool[:question_count]
                )

                st.session_state.q_index = 0
                st.session_state.score = 0

                reset_question_state()

                st.session_state.current_page = "quiz"

                st.rerun()

    st.markdown(
        """
        <div style='
            background-color:#f9fafb;
            padding:20px;
            border-radius:8px;
            color:#4b5563;
            font-size:14px;
            margin-top:20px;
        '>
        表示された成績から選手名を当てるクイズです。
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# クイズ画面
# =========================================================

def show_quiz_page():

    # -----------------------------------------
    # 中断
    # -----------------------------------------

    if st.button(
        "← 中断してスタート画面に戻る"
    ):

        st.session_state.current_page = "start"

        st.rerun()

    # -----------------------------------------
    # 選手取得
    # -----------------------------------------

    total_q = len(
        st.session_state.quiz_pool
    )

    current_idx = (
        st.session_state.q_index
    )

    player = (
        st.session_state.quiz_pool[
            current_idx
        ]
    )

    # -----------------------------------------
    # 問題番号
    # -----------------------------------------

    st.markdown(
        f"""
        <h4 style='
            text-align:center;
            color:#6b7280;
        '>
        第 {current_idx + 1} 問 / {total_q}問中
        </h4>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h2 class='title-text'
            style='font-size:24px;'>
            ⚾ この成績の選手は誰？
        </h2>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # 成績
    # =====================================================

    show_stats_card(player)

    # =====================================================
    # ヒント
    # =====================================================

    st.markdown("#### 💡 ヒント")

    if st.button(
        "所属球団を見る",
        use_container_width=True
    ):

        st.session_state.hint_team = True

    if st.session_state.hint_team:

        st.info(
            f"所属球団：{player['球団']}"
        )

    st.markdown("---")

    # =====================================================
    # 選手名検索
    # =====================================================

    st.markdown(
        "#### 選手名"
    )

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

        answer_col, skip_col = st.columns(
            [3, 1]
        )

        with answer_col:

            if st.button(
                "解答",
                type="primary",
                use_container_width=True
            ):

                if selected_player is None:

                    st.warning(
                        "選手名を検索して選択してください。"
                    )

                else:

                    input_name = normalize_name(
                        selected_player
                    )

                    correct_name = normalize_name(
                        player["選手名"]
                    )

                    if input_name == correct_name:

                        st.session_state.is_correct = True

                        st.session_state.score += 1

                    else:

                        st.session_state.is_correct = False

                    st.session_state.is_answered = True

                    st.rerun()

        with skip_col:

            if st.button(
                "分からない",
                use_container_width=True
            ):

                st.session_state.is_correct = False

                st.session_state.is_answered = True

                st.rerun()

    # =====================================================
    # 解答後
    # =====================================================

    else:

        if st.session_state.is_correct:

            st.success(
                f"🎉 大正解！"
                f" 答えは「{player['選手名']}」でした！"
            )

        else:

            st.error(
                f"残念！"
                f" 正解は「{player['選手名']}」でした。"
            )

        # -----------------------------------------
        # 次の問題
        # -----------------------------------------

        if current_idx + 1 < total_q:

            if st.button(
                "次の問題へ ➡",
                type="primary",
                use_container_width=True
            ):

                st.session_state.q_index += 1

                reset_question_state()

                st.rerun()

        # -----------------------------------------
        # 結果
        # -----------------------------------------

        else:

            if st.button(
                "結果を見る 🏆",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = "result"

                st.rerun()


# =========================================================
# 結果画面
# =========================================================

def show_result_page():

    st.markdown(
        "<h1 class='title-text'>クイズ終了！</h1>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    total_q = len(
        st.session_state.quiz_pool
    )

    score = st.session_state.score

    st.markdown(
        f"""
        <h2 style='text-align:center;'>
            {total_q}問中
            <span style='
                color:#0d9488;
                font-size:48px;
            '>
                {score}
            </span>
            問正解！
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "トップへ戻る",
        type="primary",
        use_container_width=True
    ):

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
