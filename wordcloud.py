# coding=utf-8
import jieba
import re
import time
from collections import Counter

#------------------------------------------------------------------------
cut_words = ""
all_words = ""
f = open('data-fenci.txt', 'w', encoding="utf-8")
for line in open('data.txt', encoding='utf-8'):
    line.strip('\n')
    seg_list = jieba.cut(line,cut_all=False)
    # print(" ".join(seg_list))
    cut_words = (" ".join(seg_list))
    f.write(cut_words)
    all_words += cut_words
else:
    f.close()

# output
all_words = all_words.split()
print(all_words)

# bag of words frequency
c = Counter()
for x in all_words:
    if len(x)>1 and x != '\r\n':
        c[x] += 1

# Top 10 frequency
print('\nFrequency result：')
for (k,v) in c.most_common(10):
    print("%s:%d"%(k,v))

# store the data
name = time.strftime("%Y-%m-%d") + "-fc.csv"
fw = open(name, 'w')
i = 1
for (k,v) in c.most_common(len(c)):
    fw.write(str(i)+','+str(k)+','+str(v)+'\n')
    i = i + 1
else:
    print("Over write file!")
    fw.close()

#------------------------------------wordcloud analysis------------------------------------
from pyecharts import options as opts
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType

# get data word = [('A',10), ('B',9), ('C',8)] table +Tuple
words = []
for (k,v) in c.most_common(1000):
    # print(k, v)
    words.append((k,v))

# render graph
def wordcloud_base() -> WordCloud:
    c = (
        WordCloud()
        .add("", words, word_size_range=[20, 100], shape=SymbolType.ROUND_RECT)
        .set_global_opts(title_opts=opts.TitleOpts(title='Weibo Covid-19 WordCloud'))
    )
    return c

wordcloud_base().render('Covid19_WordCloud.html')