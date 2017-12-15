# -*- coding: utf-8 -*-  
import scipy as sp  
import numpy as np  
from sklearn.datasets import load_files  
from sklearn.cross_validation import train_test_split  
from sklearn.feature_extraction.text import  TfidfVectorizer  
import jieba
  
# 加载数据集，切分数据集70%训练，30%测试
movie_reviews = load_files('comment')
doc_terms_train, doc_terms_test, y_train, y_test = train_test_split(movie_reviews.data, movie_reviews.target, test_size = 0.3)  

f = open('stopwords.txt', 'rb')
stop_words_raw = f.read()
f.close()

stop_words = stop_words_raw.split('\n')

# BOOL型特征下的向量空间模型
count_vec = TfidfVectorizer(binary = False, decode_error = 'ignore', tokenizer=jieba.cut, stop_words=stop_words)  
x_train = count_vec.fit_transform(doc_terms_train)  
x_test  = count_vec.transform(doc_terms_test)  
x       = count_vec.transform(movie_reviews.data)  
y       = movie_reviews.target
# print doc_terms_train
for word in count_vec.get_feature_names():
    print word
print x_train.toarray()