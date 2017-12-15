# -*- coding: utf-8 -*-  
import scipy as sp  
import numpy as np  
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.datasets import load_files  
from sklearn.cross_validation import train_test_split  
from sklearn.feature_extraction.text import  TfidfVectorizer  
from sklearn.feature_extraction.text import  TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
import jieba
  
movie_reviews = load_files('comment')

f = open('stopwords.txt', 'rb')
stop_words_raw = f.read()
f.close()

stop_words = stop_words_raw.split('\n')

# BOOL型特征下的向量空间模型
count_vec = CountVectorizer(binary = False, decode_error = 'ignore', tokenizer=jieba.cut, stop_words=stop_words)  
x_train_vec = count_vec.fit_transform(movie_reviews.data)

tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(x_train_vec)

# 构造 LogisticRegression 对象
kmeans = KMeans(2).fit(X_train_tfidf)
labels = kmeans.predict(X_train_tfidf)

print labels
print movie_reviews.target