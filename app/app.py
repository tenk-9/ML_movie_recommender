import streamlit as st
import pandas as pd
import numpy as np
import gensim
import os
import math

# ファイルパス定義
DIR = os.path.dirname(__file__)
# おすすめ映画の最大表示数.
# modelの語彙は9735なので，それ以下
MAX_SHOW = 2000
# 1ページ当たりの表示件数
TMP_SHOW = 10
# 表示するページ数
PAGENUM = math.ceil(MAX_SHOW/TMP_SHOW)
# 環境変数設定
if "show_cols" not in st.session_state:
    st.session_state["show_cols"] = TMP_SHOW
if "now_page" not in st.session_state:
    st.session_state["now_page"] = 1
if "prev_disabled" not in st.session_state:
    st.session_state["prev_disabled"] = True
if "next_disabled" not in st.session_state:
    st.session_state["next_disabled"] = True
# はじめのページで戻るボタン無効化
if st.session_state.now_page == 1:
    st.session_state.prev_disabled = True
    st.session_state.next_disabled = False
# 最終ページで進むボタン無効化
if st.session_state.now_page == PAGENUM:
    st.session_state.prev_disabled = False
    st.session_state.next_disabled = True
# ページめくり
def next_page():
    st.session_state.now_page += 1
    st.session_state.prev_disabled = False
def prev_page():
    st.session_state.now_page -= 1
    st.session_state.next_disabled = False
def reset_page():
    st.session_state.now_page = 1


# main
st.title('映画レコメンド')
# 映画情報の読み込み
movies = pd.read_csv(f"{DIR}/../data/movies_valid.tsv", sep="\t")

# 学習済みのitem2vecモデルの読み込み
model = gensim.models.word2vec.Word2Vec.load(f"{DIR}/../model/i2v.model")

# 映画IDとタイトルを辞書型に変換
movie_titles = movies["title"].tolist()
movie_ids = movies["movie_id"].tolist()
movie_id_to_title = dict(zip(movie_ids, movie_titles))
movie_title_to_id = dict(zip(movie_titles, movie_ids))

st.markdown("## 複数の映画を選んでおすすめの映画を表示する")
st.markdown("**好きな映画と嫌いな映画から，気に入りそうな映画を表示します！**")
# 好きな映画のmultiselectと嫌いな映画のmultiselectを並べる
positive_holder, negative_holder = st.columns(2)
with positive_holder:
    positive_movies = st.multiselect(
        label=":red[好きな映画]を複数選んでください", 
        options=movie_titles,
        placeholder="Choose positive movies",
        on_change=reset_page,
        )
with negative_holder:
    negative_movies = st.multiselect(
        label=":blue[嫌いな映画]を複数選んでください", 
        options=movie_titles,
        placeholder="Choose negative movies",
        on_change=reset_page,
        )
# st.multiselectでは，選択した要素名(ここでは映画のタイトル)が戻ってくる
# -> 好きな映画と嫌いな映画，それぞれをid化
positive_movie_ids = [movie_title_to_id[movie] for movie in positive_movies]
negative_movie_ids = [movie_title_to_id[movie] for movie in negative_movies]
# おすすめ映画を抽出
st.markdown(f"### おすすめの映画")
recommend_holder = st.empty()
recommend_results = []
recommend_df_cols = ["rank","movie_id","title","score"]
if len(positive_movies) > 0:
    similars = model.wv.most_similar(
        positive=positive_movie_ids,
        negative=negative_movie_ids,
        topn=MAX_SHOW,
        )
    # 順位もつけることにする
    for rank, (movie_id, score) in enumerate(similars):
        title = movie_id_to_title[movie_id]
        recommend_results.append({"rank":rank+1,
                                  "movie_id":movie_id,
                                  "title": title,
                                  "score": score})
    # TMP_SHOW件にトリミング
    recommend_results = recommend_results[
        (st.session_state.now_page-1)*TMP_SHOW:(st.session_state.now_page)*TMP_SHOW
        ]
        
recommend_results = pd.DataFrame(recommend_results, columns=recommend_df_cols)
recommend_results = recommend_results.set_index("rank")
recommend_holder.dataframe(recommend_results,use_container_width=True)

# 戻るボタン，現在のページ，進むボタン
prev_btn, current_page, next_btn = st.columns(3)
with current_page:
    if len(recommend_results) == 0:
        st.session_state.prev_disabled = True
        st.session_state.next_disabled = True
        st.markdown(f"0/0")
    else:
        st.markdown(f"{st.session_state.now_page}/{PAGENUM}")
with prev_btn:
    st.button(
        label="<PREV",
        on_click=prev_page,
        disabled=st.session_state.prev_disabled,
    )
with next_btn:
    st.button(
        label="NEXT>",
        on_click=next_page,
        disabled=st.session_state.next_disabled,
    )
