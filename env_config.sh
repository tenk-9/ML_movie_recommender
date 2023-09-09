# download and unzip dataset
wget -nc --no-check-certificate https://files.grouplens.org/datasets/movielens/ml-10m.zip -P data/
unzip -n data/ml-10m.zip -d data/
# install required packages
pip install -r requirements.txt