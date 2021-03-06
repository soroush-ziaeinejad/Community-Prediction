import gensim
import networkx as nx
import time
import pandas as pd
import datetime
import os
import numpy as np
import TopicModeling as TM
import UsersGraph as UG

# Changing saves location
now = datetime.datetime.now()
dt_string = now.strftime("%Y_%m_%d__%H_%M")
if not os.path.exists('run_outputs'):
    os.mkdir('run_outputs')
os.chdir('run_outputs')
os.mkdir(dt_string)
os.chdir(dt_string)




# def Doc2Topic(ldaModel, docs):
#     doc_topic = []
#     doc_topic = np.zeros((len(docs), ldaModel.num_topics))
#     counter = 0
#     for doc in docs:
#         doc_topic_vector = np.zeros((ldaModel.num_topics))
#         try:
#             d2tVector = ldaModel.get_document_topics(doc)
#         except:
#             gen_model = gensim.models.wrappers.ldamallet.malletmodel2ldamodel(ldaModel)
#             d2tVector = gen_model.get_document_topics(doc)
#         for i in d2tVector:
#             doc_topic_vector[i[0]] = i[1]
#         doc_topic.append(doc_topic_vector)
#     doc_topic = np.asarray(doc_topic)
#     return doc_topic


def Doc2Topic(ldaModel, doc, threshold=0.2):
    doc_topic_vector = np.zeros((ldaModel.num_topics))
    try:
        d2tVector = ldaModel.get_document_topics(doc)
    except:
        gen_model = gensim.models.wrappers.ldamallet.malletmodel2ldamodel(ldaModel)
        d2tVector = gen_model.get_document_topics(doc)
    for i in d2tVector:
        if i[1] >= threshold:
            doc_topic_vector[i[0]] = i[1]
    # doc_topic_vector = np.asarray(doc_topic_vector)
    return doc_topic_vector

print('Topic modeling started')
topic_num = 28
TopicModel = TM.topic_modeling(num_topics=topic_num, filterExtremes=True, library='gensim')
print('Topic modeling finished')
dictionary, bow_corpus, totalTopics, lda_model, num_topics, processed_docs, documents = TopicModel
start_date = documents['CreationDate'].min()
end_date = documents['CreationDate'].max()
# day = start_date
day = end_date - pd._libs.tslibs.timestamps.Timedelta(days=10)
total_users_topic_interests = []
all_users = documents['userId']
users_topic_interests = np.zeros((len(all_users), topic_num))
print(users_topic_interests.shape)
users_Ids = []
max_users = 0

while day <= end_date:
    c = documents[(documents['CreationDate'] == day)]
    print(str(len(c)) + ' users has twitted in '+str(day))
    # total_users_topic_interests.append([])
    texts = c['Text']
    users = c['userId']
    # for userTextidx in range(len(all_users)):
    for userTextidx in range(min(300, len(c['Text']))):
        doc = texts.iloc[userTextidx]
        user_bow_corpus = dictionary.doc2bow(doc.split(','))
        # tic = time.clock()
        D2T = Doc2Topic(lda_model, user_bow_corpus, threshold=0.4)
        # toc = time.clock()
        # print('D2T function takes', toc-tic, 'seconds for ')
        # users_topic_interests[-1].append(D2T)
        users_topic_interests[users.keys()[userTextidx]] = D2T
        users_Ids.append(users.iloc[userTextidx])
    total_users_topic_interests.append(users_topic_interests)
    # print(c.shape)
    day = day + pd._libs.tslibs.timestamps.Timedelta(days=1)
total_users_topic_interests = np.asarray(total_users_topic_interests)
graphs = []
for day in range(len(total_users_topic_interests)):
    if day % 2 == 0 or True:
        print(day, '/', len(total_users_topic_interests))
    graph = UG.CreateUsersGraph(day, users_Ids, total_users_topic_interests[day], max_users, all_users)
    graphs.append(graph)
print('Graph Created!')
os.mkdir('graphs')
os.chdir('graphs')
for i in range(len(graphs)):
    if i < 9:
        nx.write_gpickle(graphs[i], '0'+str(i+1)+'.net')
    else:
        nx.write_gpickle(graphs[i], str(i+1)+'.net')

# print('Document to topics transformation:')
# There are two options here. One is aggregating dataset again with whole tweets of a user and give it to the Doc2Topic. Two is apply some functions
# like max or mean on the percentage of interests.

# ## METHOD 1:
# dataGroupbyUsers = documents.groupby(['userId'])
# documents = dataGroupbyUsers['Text'].apply(lambda x: '\n'.join(x)).reset_index()
# bow_corpus = [dictionary.doc2bow(doc) for doc in documents]
# D2T = Doc2Topic(lda_model, bow_corpus)
# np.save('Docs2Topics.npy', D2T)
#
# ## METHOD 2:
# D2T = Doc2Topic(lda_model, bow_corpus)
# userset = np.asarray(documents['userId'])
# userset_distinct = np.sort(np.asarray(list(set(userset))))
# for userId in userset_distinct:
#     indices = np.where(userset == userId)[0]
#     ThisUserMatrix = D2T[indices.min():indices.max]
#     # Aggregation Method: Mean, Max, Whatever...




# num_users = len(documents['userId'])
# user_user_matrix = np.zeros((num_users, num_users))
