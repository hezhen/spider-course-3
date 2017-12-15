import jieba

text = '分布式爬虫是包含了分布式存储、任务管理、分布式数据库和爬虫进程的一套数据抓取系统'

words = list(jieba.cut(text))

print ','.join(words)