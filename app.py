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

    required_batter = [
        "選手名", "球団", "試合数", "打席数",
        "打率", "本塁打", "打点", "盗塁", "OPS"
    ]

    required_pitcher = [
        "選手名", "球団", "登板数", "投球回",
        "防御率", "勝利", "奪三振", "勝率", "WHIP"
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
