import streamlit as st
import pandas as pd
import random
import re
import unicodedata

# =========================================================
# 1. データの読み込み
# =========================================================
@st.cache_data
def load_data():
    file_name = "baseball_data.xlsx"

    try:
        dfs = pd.read_excel(file_name, sheet_name=None)
    except FileNotFoundError:
        st.error(
            f"🚨 【エラー】同じフォルダに `{file_name}` が見つかりません。"
            "ファイル名や保存場所を確認してください。"
        )
        st.stop()
    except Exception as e:
        st.error(f"🚨 【エラー】ファイルの読み込みに失敗しました: {e}")
        st.stop()

    # シート名チェック
    if "野手" not in dfs or "投手" not in dfs:
        st.error(
            "🚨 【エラー】Excelファイル内に「野手」と「投手」の"
            "シート（タブ）が揃っていません。"
        )
        st.stop()

    # 野手に必要な列
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

    # 投手に必要な列
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
        "奪三振",
        "勝率",
        "WHIP"
    ]

    missing_b = [
        col for col in required_batter
        if col not in dfs["野手"].columns
    ]

    missing_p = [
        col for col in required_pitcher
        if col not in dfs["投手"].columns
    ]

    if missing_b or missing_p:

        if missing_b:
            st.error(
                "🚨 【エラー】「野手」シートに以下の列がありません: "
                + ", ".join(missing_b)
            )

        if missing_p:
            st.error(
                "🚨 【エラー】「投手」シートに以下の列がありません: "
                + ", ".join(missing_p)
            )

        st.info(
            "💡 Excelの1行目（ヘッダー）の文字が、必要な列名と"
            "完全に一致しているか確認してください。"
        )
        st.stop()

    # =====================================================
    # 数値列を数値化
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

    # 欠損値処理
    for sheet in dfs:
        dfs[sheet] = dfs[sheet].fillna("-")

    return dfs


dfs = load_data()


# =========================================================
# 2. セッション状態
# =========================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "start"

if "quiz_pool" not in st.session_state:
    st.session_state.quiz_pool = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0


def reset_question_state():
    st.session_state.hint_team = False
    st.session_state.is_answered = False
    st.session_state.is_correct = False


if "is_answered" not in st.session_state:
    reset_question_state()


# =========================================================
# 3. 選手名の比較処理
# =========================================================
def normalize_name(text):
    """
    選手名比較用
    ・全角/半角を統一
    ・空白を除去
    """

    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", "", text)

    return text.strip()


# =========================================================
# 4. CSS
# =========================================================
st.markdown(
    """
    <style>

    .title-text {
        text-align: center;
        color: #1f2937;
        margin-bottom: 0px;
        font-weight: 800;
        font-size: 32px;
    }

    .sub-text {
        text-align: center;
        color: #6b7280;
        font-size: 14px;
    }

    .link-text {
        text-align: center;
        color: #0d9488;
        font-size: 14px;
        margin-bottom: 20px;
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
    """,
    unsafe_allow_html=True
)


# =========================================================
# 5. スタート画面
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

    st.markdown(
        "<p class='link-text'>ランキングを見る</p>",
        unsafe_allow_html=True
    )

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
            "※選択したレギュレーションの対象選手で絞り込みます"
            "</div>",
            unsafe_allow_html=True
        )

        with st.expander("フィルター", expanded=False):

            min_pa = st.number_input(
                "最低打席数の制限",
                min_value=0,
                value=0,
                step=50
            )

            min_ip = st.number_input(
                "最低投球回数の制限",
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

            # セ・リーグ
            central = [
                "阪神",
                "広島",
                "DeNA",
                "巨人",
                "ヤクルト",
                "中日"
            ]

            # パ・リーグ
            pacific = [
                "オリックス",
                "ロッテ",
                "ソフトバンク",
                "楽天",
                "西武",
                "日本ハム"
            ]

            scopes = selected_scopes if selected_scopes else []

            is_all = (
                "全て" in scopes
                or len(scopes) == 0
            )

            # =================================================
            # リーグの絞り込み
            # =================================================

            if is_all or (
                "セ" not in scopes
                and "パ" not in scopes
            ):

                allowed_leagues = central + pacific

            else:

                allowed_leagues = []

                if "セ" in scopes:
                    allowed_leagues.extend(central)

                if "パ" in scopes:
                    allowed_leagues.extend(pacific)

            # =================================================
            # 投手・野手の絞り込み
            # =================================================

            if is_all or (
                "野手" not in scopes
                and "投手" not in scopes
            ):

                allowed_roles = [
                    "野手",
                    "投手"
                ]

            else:

                allowed_roles = []

                if "野手" in scopes:
                    allowed_roles.append("野手")

                if "投手" in scopes:
                    allowed_roles.append("投手")

            pool = []

            # =================================================
            # 野手
            # =================================================

            if "野手" in allowed_roles:

                b_df = dfs["野手"].copy()

                filtered_b = b_df[
                    (b_df["球団"].isin(allowed_leagues))
                    &
                    (b_df["打席数"] >= min_pa)
                ]

                for _, row in filtered_b.iterrows():

                    player = row.to_dict()

                    player["type"] = "野手"

                    pool.append(player)

            # =================================================
            # 投手
            # =================================================

            if "投手" in allowed_roles:

                p_df = dfs["投手"].copy()

                filtered_p = p_df[
                    (p_df["球団"].isin(allowed_leagues))
                    &
                    (p_df["投球回"] >= min_ip)
                ]

                for _, row in filtered_p.iterrows():

                    player = row.to_dict()

                    player["type"] = "投手"

                    pool.append(player)

            # =================================================
            # 出題可能選手がいない場合
            # =================================================

            if len(pool) == 0:

                st.error(
                    "条件に合う選手がいません！"
                    "フィルターを緩めてください。"
                )

                return

            # 問題順をランダム化
            random.shuffle(pool)

            if q_count_str == "エンドレス":

                max_q = len(pool)

            else:

                max_q = min(
                    int(q_count_str.replace("問", "")),
                    len(pool)
                )

            st.session_state.quiz_pool = pool[:max_q]

            st.session_state.score = 0

            st.session_state.q_index = 0

            reset_question_state()

            st.session_state.current_page = "quiz"

            st.rerun()

    st.markdown(
        """
        <div style='background-color: #f9fafb;
                    padding: 20px;
                    border-radius: 8px;
                    color: #4b5563;
                    font-size: 14px;
                    margin-top: 20px;'>

        成績クイズは、表示された成績の数字から
        選手名を当てるクイズです。

        打席数や投球回数のフィルターを活用して
        難易度を調整できます。

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 6. クイズ画面
# =========================================================
def show_quiz_page():

    # 問題がない場合
    if not st.session_state.quiz_pool:

        st.session_state.current_page = "start"
        st.rerun()

    # 中断
    if st.button("← 中断してスタート画面に戻る"):

        st.session_state.current_page = "start"
        st.rerun()

    total_q = len(st.session_state.quiz_pool)

    current_idx = st.session_state.q_index

    # 範囲外防止
    if current_idx >= total_q:

        st.session_state.current_page = "result"
        st.rerun()

    player = st.session_state.quiz_pool[current_idx]

    # =====================================================
    # 問題番号
    # =====================================================

    st.markdown(
        f"<h4 style='text-align: center; color: #6b7280;'>"
        f"第 {current_idx + 1} 問 / {total_q}問中"
        f"</h4>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 class='title-text' "
        "style='font-size: 24px; margin-bottom: 20px;'>"
        "⚾ この成績の選手は誰？"
        "</h2>",
        unsafe_allow_html=True
    )

    # =====================================================
    # 成績表示
    # =====================================================

    with st.container(border=True):

        # -------------------------------------------------
        # 野手
        # -------------------------------------------------

        if player["type"] == "野手":

            # 1段目
            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "試合数",
                f"{player['試合数']}"
            )

            c2.metric(
                "打席数",
                f"{player['打席数']}"
            )

            c3.metric(
                "打率",
                f"{player['打率']}"
            )

            c4.metric(
                "本塁打",
                f"{player['本塁打']}"
            )

            # 2段目
            c5, c6, c7 = st.columns(3)

            c5.metric(
                "打点",
                f"{player['打点']}"
            )

            c6.metric(
                "盗塁",
                f"{player['盗塁']}"
            )

            c7.metric(
                "OPS",
                f"{player['OPS']}"
            )

        # -------------------------------------------------
        # 投手
        # -------------------------------------------------

        else:

            # 1段目
            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "登板数",
                f"{player['登板数']}"
            )

            c2.metric(
                "防御率",
                f"{player['防御率']}"
            )

            c3.metric(
                "勝利",
                f"{player['勝利']}"
            )

            c4.metric(
                "敗北",
                f"{player['敗北']}"
            )

            # 2段目
            c5, c6, c7 = st.columns(3)

            c5.metric(
                "セーブ",
                f"{player['セーブ']}"
            )

            c6.metric(
                "HP",
                f"{player['HP']}"
            )

            c7.metric(
                "奪三振",
                f"{player['奪三振']}"
            )

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
            f"所属球団: {player['球団']}"
        )

    st.markdown("---")

    # 回答入力
st.markdown("### 回答")

answer_key = f"answer_{st.session_state.q_index}"

answer = st.text_input(
    "選手名を入力してください",
    key=answer_key,
    placeholder="例：村上、佐藤輝明"
)

# =========================
# 全選手から検索候補を表示
# =========================
if answer:
    normalized_answer = normalize_name(answer)

    all_names = []

    # 野手・投手の両方から全選手を取得
    for sheet_name in ["野手", "投手"]:
        if sheet_name in dfs:
            for name in dfs[sheet_name]["選手名"]:
                name = str(name).strip()

                if name and name != "-" and name not in all_names:
                    all_names.append(name)

    # 入力文字を含む選手を検索
    candidates = [
        name for name in all_names
        if normalized_answer in normalize_name(name)
    ]

    if candidates:
        st.markdown("**検索候補**")

        # 最大10人まで表示
        for i, candidate in enumerate(candidates[:10]):
            if st.button(
                candidate,
                key=f"candidate_{st.session_state.q_index}_{i}",
                use_container_width=True
            ):
                st.session_state[answer_key] = candidate
                st.rerun()

        # -------------------------------------------------
        # 解答
        # -------------------------------------------------

        with ans_col:

            if st.button(
                "解答する",
                type="primary",
                use_container_width=True
            ):

                clean_input = normalize_name(
                    answer_input
                )

                correct_answer = normalize_name(
                    player["選手名"]
                )

                if clean_input == "":

                    st.warning(
                        "選手名を入力してください。"
                    )

                    return

                if clean_input == correct_answer:

                    st.session_state.is_correct = True

                    st.session_state.score += 1

                else:

                    st.session_state.is_correct = False

                st.session_state.is_answered = True

                st.rerun()

        # -------------------------------------------------
        # 分からない
        # -------------------------------------------------

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
                f"🎉 大正解！ 答えは"
                f"「{player['選手名']}」でした！"
            )

        else:

            st.error(
                f"残念！ 正解は"
                f"「{player['選手名']}」でした。"
            )

        # =================================================
        # 次の問題
        # =================================================

        if current_idx + 1 < total_q:

            if st.button(
                "次の問題へ ➡",
                type="primary",
                use_container_width=True
            ):

                st.session_state.q_index += 1

                reset_question_state()

                st.rerun()

        # =================================================
        # 結果
        # =================================================

        else:

            if st.button(
                "結果を見る 🏆",
                type="primary",
                use_container_width=True
            ):

                st.session_state.current_page = "result"

                st.rerun()


# =========================================================
# 7. 結果画面
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
        f"<h2 style='text-align: center;'>"
        f"{total_q}問中 "
        f"<span style='color: #0d9488; font-size: 48px;'>"
        f"{score}</span> 問正解！"
        f"</h2>",
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
# 8. 画面ルーティング
# =========================================================
if st.session_state.current_page == "start":

    show_start_page()

elif st.session_state.current_page == "quiz":

    show_quiz_page()

elif st.session_state.current_page == "result":

    show_result_page()
