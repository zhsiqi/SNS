#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 16:48:52 2021

@author: zhangsiqi
"""

import pandas as pd
from collections import Counter
import igraph as ig
import re

# 读取csv文件，合并‘博文’与‘原文’一列成为新行，将合并结果保存为csv文件
data = pd.read_csv('sampledata.csv', lineterminator="\n")
data['合并'] = data['博文'].astype(str) + data['原文'].astype(str)
data.to_csv("alldata.csv", index = False)

repo = Counter()
ids = []
posts = []
relations = []

#找到节点和边
for text in data['合并']:
    names = re.findall('(//|回复)(@.+?[：:\\s])',text)
    # 当帖子中有2个及以上的id时，用列表保存该帖子的传播链
    if len(names) > 1:
        flow = []
        
        #print('names', names)
        for i in names:
            id = i[1].strip().strip(':').strip('：').strip('@')
            flow.append(id) #保存转发链
        if len(list(set(flow))) > 1:
            posts.append(text)
            relations.append(flow)
            #data1[text] = str(flow)
        # print(n, 'flow', flow)
        for j in range(len(flow)-1):
            if flow[j] != flow[j+1]: #剔除自我转发和自我回复
                ids.append(flow[j]) 
                ids.append(flow[j+1])
                repo[(flow[j], flow[j+1])] += 1 #在计数器中保存转发对子的频次

print(sum(repo.values()))

# 创建数据框
data1 = {'posts':posts, 'relations':relations}
d1 = pd.DataFrame(data1)
print(d1)

# 将数据导出
d1.to_excel("测试3.xlsx")

# 创建一个有向的网络对象
g = ig.Graph(directed=True)

# 在网络中批量添加用户id节点
users = list(set(ids)) # 用集合去除重复的id，并转换为列表
g.add_vertices(users)

# 在网络中添加转发关系作为边
g.add_edges(repo.keys())
#g.add_edges(pairs) ## add an edge from Tom to John

# 添加转发频次作为边的强度属性
g.es['strength'] = list(repo.values())

print(g.summary())

# 成分分析
cps = g.components(mode='weak') 
print(sorted(cps.sizes(), reverse = True)) 
print(len(cps.sizes()))

# 各成分差距过于悬殊，选择最大的成分进行分析
topg = cps.giant()
print(topg.summary()) 
print(topg.es['strength'])


strelist = topg.es['strength']
print(type(strelist))
print(sorted(strelist, reverse = True))
print(strelist.count(1))
print(sum(strelist))
print(len(strelist))

# community detection
sgcom = topg.community_spinglass()
print(sgcom.summary())
print(sorted(sgcom.sizes(), reverse = True))

#为节点增加社群的属性
sgcom.membership
topg.vs['community'] = sgcom.membership 

topg.save("topg.graphml")

#描述网络
print(topg.density()) #密度
topg.dyad_census() #对普查，结果147, 2177, 2046976
print(sorted(topg.betweenness(), reverse=True))
