import MySQLdb
import Levenshtein
import networkx as nx
import datetime as dt
import threading
import wikipedia
from getcan import *

def getEntity(mention,entityname):
	candidatelist = []
	if mention == '':
		return candidatelist
	else:
		conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
		cur = conn.cursor()

		mysql = "select entitystr from labels  where entityname LIKE (\""+mention+"\") limit 7"
		#mysql = "select entityname from labels  where match(entitystr) against (\""+mention+"\" in boolean mode) limit 4"
		cur.execute(mysql)
		resultlist = cur.fetchall()
		for each in resultlist:
			if "_(" + mention + ")" in each[0]:
				continue
			if entityname.lower() == each[0].lower():
				continue
			candidatelist.append(each[0])
		if entityname in candidatelist:
			pass
		else:
			candidatelist.append(entityname)

		mysql = "select redirectname from redirect  where entityname LIKE (\"" + mention + "\") limit 7"
		cur.execute(mysql)
		resultlist = cur.fetchall()
		for each in resultlist:
			if "_(" + mention + ")" in each[0]:
				continue
			if entityname.lower() == each[0].lower():
				continue
			candidatelist.append(each[0])
		if entityname in candidatelist:
			pass
		else:
			candidatelist.append(entityname)

		mysql = "select disname from disambiguations  where entityname LIKE (\"" + mention + "\") limit 7"
		cur.execute(mysql)
		resultlist = cur.fetchall()
		for each in resultlist:
			if "_(" + mention + ")" in each[0]:
				continue
			if entityname.lower() == each[0].lower():
				continue
			candidatelist.append(each[0])
		if entityname in candidatelist:
			pass
		else:
			candidatelist.append(entityname)

		cur.close()
		conn.commit()
		conn.close()
		return candidatelist

def getEntity1(mention):
	candidatelist = []
	if mention == '':
		return candidatelist
	else:
		conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
		cur = conn.cursor()
		mysql = "select entityname from labels  where match(entitystr) against (\""+mention+"\" in natural language mode) limit 7"
		#mysql = "select entityname from labels  where match(entitystr) against (\""+mention+"\" in boolean mode) limit 4"
		cur.execute(mysql)
		resultlist = cur.fetchall()
		for each in resultlist:
			candidatelist.append(each[0])
		cur.close()
		conn.commit()
		conn.close()
		candidatelist1 = []
		for can in candidatelist:
			num = 0
			for can1 in candidatelist1:
				if can.lower() == can1.lower():
					num += 1
					break
			if num == len(candidatelist1):
				candidatelist1.append(can)
		return candidatelist1

def getentitybywiki(mention,maxnum):
	resultlist = wikipedia.search(mention,results=maxnum)
	returnlist = []
	for each in resultlist:
		returnlist.append("_".join(each.encode("utf-8").split()))
	return returnlist

class getEntityByWiki(threading.Thread):
	def __init__(self,mention,maxnum):
		threading.Thread.__init__(self)
		self.mention = mention
		self.maxnum = maxnum
		self.resultlist = []

	def run(self):
		self.resultlist = getentitybywiki(self.mention,self.maxnum)

def getCandidate():
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
	cur = conn.cursor()
	stmt1 = "select distinct docid from test"
	cur.execute(stmt1)
	docs = cur.fetchall()
	entitydoc = []
	for doc in docs:
		entitydoc.append(doc[0])

	docmention = {}
	for doc in entitydoc:
		sql = "select mention,entityname from test where docid = \"" + doc + "\""
		cur.execute(sql)
		result = cur.fetchall()
		mentionlist = []
		for mention,entityname in result:
			mentionlist.append([mention,entityname])
		docmention[doc] = mentionlist

	doccandidate = {}
	'''下面这个是我自己加的'''
	entitydics = {}

	for doc in entitydoc:
		mentionlist = docmention[doc]#0:mention 1:targetentity
		entitydic = {}
		for mention,entityname in mentionlist:
			candidatelist = getEntity(mention,entityname)
			entitydic[mention] = candidatelist
		doccandidate[doc] = [entitydic,mentionlist]
		print (doc)
		print (entitydic)
		entitydics[doc] = [entitydic]
	entitydicsvalue = entitydics.values()
	#print("entitydicsvalue=" + str(entitydicsvalue))
	return entitydoc,doccandidate,entitydicsvalue

def getCandidateByWiki():
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
	cur = conn.cursor()
	stmt1 = "select distinct docid from test"
	cur.execute(stmt1)
	docs = cur.fetchall()
	entitydoc = []
	for doc in docs:
		entitydoc.append(doc[0])

	docmention = {}
	for doc in entitydoc:
		sql = "select mention,entityname from test where docid = \"" + doc + "\""
		cur.execute(sql)
		result = cur.fetchall()
		mentionlist = []
		for mention,entityname in result:
			mentionlist.append([mention,entityname])
		docmention[doc] = mentionlist

	doccandidate = {}
	for doc in entitydoc:
		threads = []
		resultlist = []
		mentionlist = docmention[doc]
		for mention,entity in mentionlist:
			threads.append(getEntityByWiki(mention,5))
		for t in threads:
			t.start()
		for t in threads:
			t.join()
			resultlist.append(t.resultlist)
		entitydic = {}
		for i in range(len(mentionlist)):
			entitydic[mentionlist[i][0]] = resultlist[i]
			if resultlist[i]==[]:
				entitydic[mentionlist[i][0]] = getEntity1(mentionlist[i][0])
		doccandidate[doc] = [entitydic,mentionlist]
		print (doc)
		print (entitydic)
	return entitydoc,doccandidate

def getCandidateByRule():	 	
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
	cur = conn.cursor()
	stmt1 = "select distinct docid from test"
	cur.execute(stmt1)
	docs = cur.fetchall()
	entitydoc = []
	for doc in docs:
		entitydoc.append(doc[0])

	docmention = {}
	for doc in entitydoc:
		sql = "select mention,entityname from test where docid = \"" + doc + "\""
		cur.execute(sql)
		result = cur.fetchall()
		mentionlist = []
		for mention,entityname in result:
			mentionlist.append([mention,entityname])
		docmention[doc] = mentionlist

	doccandidate = {}
	for doc in entitydoc:
		mentionlist = docmention[doc]#0:mention 1:targetentity
		entitydic = {}
		for mention,entityname in mentionlist:
			candidatelist = getCanByRule(mention)
			entitydic[mention] = candidatelist
		doccandidate[doc] = [entitydic,mentionlist]
		print(doc)
		print(entitydic)
	return entitydoc,doccandidate

def getCandidateByPriorRule():
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
	cur = conn.cursor()
	stmt1 = "select distinct docid from test"
	cur.execute(stmt1)
	docs = cur.fetchall()
	entitydoc = []
	for doc in docs:
		entitydoc.append(doc[0])

	docmention = {}
	for doc in entitydoc:
		sql = "select mention,entityname from test where docid = \"" + doc + "\""
		cur.execute(sql)
		result = cur.fetchall()
		mentionlist = []
		for mention,entityname in result:
			mentionlist.append([mention,entityname])
		docmention[doc] = mentionlist

	doccandidate = {}
	for doc in entitydoc:
		mentionlist = docmention[doc]#0:mention 1:targetentity
		entitydic = {}
		for mention,entityname in mentionlist:
			candidatelist = getCanByPriorRule(mention)
			entitydic[mention] = candidatelist
		doccandidate[doc] = [entitydic,mentionlist]
		print(doc)
		print(entitydic)
	return entitydoc,doccandidate

def getCandidateSet(mentioncanlist):
	candidatelist = []
	for mentioncan in mentioncanlist:
		candidatelist.extend(mentioncan[1])
	return candidatelist

#get no directed pair 
def getEntityPair1(entitydic):
	entitypairarray = []
	for entity1 in entitydic.keys():
		for entity2 in entitydic.keys():
			if entity1 != entity2:
				for each1 in entitydic[entity1]:
					for each2 in entitydic[entity2]:
						entitypairarray.append([each1,each2])
	entitypairarraynew = []
	for entitypair in entitypairarray:
		entity1,entity2 = entitypair
		if [entity2,entity1] not in entitypairarraynew:
			entitypairarraynew.append(entitypair)
	return entitypairarraynew

#get the directed pair
def getEntityPair(entitydic,doccandidate):
	entitypairarray = []

	for entity1 in entitydic.keys():
		for entity2 in entitydic.keys():
			if entity1 != entity2:
				for each1 in entitydic[entity1]:
					for each2 in entitydic[entity2]:
						entitypairarray.append([each1,each2])
	return entitypairarray

def getSQL(entitypair,len):#
	mysql = 'select a.entityname,a.linkname'
	for i in range(len-1):
		mysql = mysql + ',' + chr(98+i) +'.linkname'
	mysql = mysql + ' from pagelinks as a '
	for i in range(len-1):
		mysql = mysql + 'join pagelinks as ' + chr(98+i) + ' '
	mysql = mysql + "where a.entityname = \""+entitypair[0]+"\" and " + chr(98+len-2) + ".linkname = \""+entitypair[1]+"\""
	for i in range(len-1):
		mysql = mysql + ' and ' + chr(98+i-1) + '.linkname = ' + chr(98+i) + '.entityname'
	return mysql

# a way that are just suitable for path of 2
def getPairPath(entitypair):
	if "\"" in entitypair[0]:
		entitypair[0] = entitypair[0].replace("\"","")
	if "\"" in entitypair[1]:
		entitypair[1] = entitypair[1].replace("\"","")
	"mysql1:a->b"
	"mysql2:a<-b"
	"mysql3:a->()->b"
	"mysql4:a<-()<-b"
	"mysql5:a->()<-b"
	"mysql6:a<-()->b"
	patharray = []
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',port=3306,charset='utf8')
	cur = conn.cursor()
	mysql1 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[0]+"\" and linkname = \""+entitypair[1]+"\""
	mysql2 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[1]+"\" and linkname = \""+entitypair[0]+"\""
	mysql3 = "select a.entityname,a.linkname,b.linkname from pagelinks as a join pagelinks as b where a.entityname=%s and a.linkname = b.entityname and b.linkname=%s"
	mysql4 = "select b.entityname,b.linkname,a.linkname from pagelinks as a join pagelinks as b where a.linkname=%s and b.linkname = a.entityname and b.entityname=%s"
	mysql5 = "select a.linkname from pagelinks as a join pagelinks as b where a.entityname=%s and b.linkname=a.linkname and b.entityname=%s"
	mysql6 = "select a.entityname from pagelinks as a join pagelinks as b where a.linkname=%s and b.entityname=a.entityname and b.linkname=%s"
	cur.execute(mysql1)
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	cur.execute(mysql2)
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	cur.execute(mysql3,(entitypair[0],entitypair[1]))
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	cur.execute(mysql4,(entitypair[0],entitypair[1]))
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	cur.execute(mysql5,(entitypair[0],entitypair[1]))
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append((entitypair[0],eachresult[0]))
		patharray.append((entitypair[1],eachresult[0]))
	cur.execute(mysql6,(entitypair[0],entitypair[1]))
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		patharray.append((eachresult[0],entitypair[0]))
		patharray.append((eachresult[0],entitypair[1]))
	return patharray

def getPairArrayPath(entitypairarray):
	patharray = []
	for entitypair in entitypairarray:
		path = getPairPath(entitypair)
		patharray.extend(path)
	return patharray

def getPairPath1(entitypair):
	if "\"" in entitypair[0]:
		entitypair[0] = entitypair[0].replace("\"","")
	if "\"" in entitypair[1]:
		entitypair[1] = entitypair[1].replace("\"","")
	patharray = []
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',port=3306,charset='utf8')
	cur1 = conn.cursor()
	cur2 = conn.cursor()
	cur3 = conn.cursor()
	cur4 = conn.cursor()
	mysql1 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[0]+"\" and linkname = \""+entitypair[1]+"\""
	mysql2 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[1]+"\" and linkname = \""+entitypair[0]+"\""
	mysql3 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[0]+"\""
	mysql4 = "select entityname,linkname from pagelinks where entityname = \""+entitypair[1]+"\""
	cur1.execute(mysql1)
	resultlist = cur1.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	cur2.execute(mysql2)
	resultlist = cur2.fetchall()
	for eachresult in resultlist:
		patharray.append(eachresult)
	linkset1 = []
	linkset2 = []
	cur3.execute(mysql3)
	resultlist = cur3.fetchall()
	for eachresult in resultlist:
		linkset1.append(eachresult)
	cur4.execute(mysql4)
	resultlist = cur4.fetchall()
	for eachresult in resultlist:
		linkset2.append(eachresult)
	for entityname1,linkname1 in linkset1:
		for entityname2,linkname2 in linkset2:
			if linkname1 == linkname2:
				print (entityname1,linkname1)
				print('***************************')
				print (entityname2,linkname2)
				patharray.append((entityname1,linkname1))
				patharray.append((entityname2,linkname2))
	return patharray



def getPairArrayPath1(entitypairarray):
	patharray = []
	for entitypair in entitypairarray:
		path = getPairPath1(entitypair)
		patharray.extend(path)
	return patharray

def getPairPath2(entitypair,len):
	patharray = []
	conn= MySQLdb.connect(host='localhost',user='root',passwd = '123',db ='entitylinkdb',charset='utf8')
	cur = conn.cursor()
	mysql = getSQL(entitypair,len)
	cur.execute(mysql)
	resultlist = cur.fetchall()
	for eachresult in resultlist:
		print (eachresult)
		patharray.append(eachresult)
	return patharray

def getPairArrayPath2(entitypairarray,len):
	patharray = []
	for entitypair in entitypairarray:
		path = getPairPath2(entitypair,len)
		patharray.extend(path)
	return patharray

def getEdges(patharray):
	edges = []
	nodes = []
	for eachpath in patharray:
		for i in range(len(eachpath)-1):
			edges.append((eachpath[i],eachpath[i+1]))
		for node in eachpath:
			nodes.append(node)
	nodes = list(set(nodes))
	edges = list(set(edges))
	return edges,nodes

def getGraphByStandardPagelink(entitydic,edges,nodes):
	G = nx.DiGraph()
	G.add_nodes_from(nodes)
	G.add_edges_from(edges)
	#nx.draw(G,with_labels = True)
	#plt.show()
	pr = nx.pagerank(G)
	predict = {}
	for key in entitydic.keys():
		if entitydic[key] == []:
			predict[key] = "NULL"
		else:
			value = 0
			for canentity in entitydic[key]:
				entityvalue = pr[canentity]
				if entityvalue>value:
					value = entityvalue
					predictentity = canentity
			predict[key] = predictentity
	return predict

def getGraphByStandardPagelink1(entitydic,edges,nodes):
	G = nx.Graph()
	G.add_nodes_from(nodes)
	G.add_edges_from(edges)
	#nx.draw(G,with_labels = True)
	#plt.show()
	pr = nx.pagerank(G)
	predict = {}
	for key in entitydic.keys():
		if entitydic[key] == []:
			predict[key] = "NULL"
		else:
			value = 0
			for canentity in entitydic[key]:
				entityvalue = pr[canentity]
				if entityvalue>value:
					value = entityvalue
					predictentity = canentity
			predict[key] = predictentity
	return predict
	
def getGraphByGreedSearch(entitydic,edges,nodes):
	G = nx.DiGraph()
	G.add_nodes_from(nodes)
	G.add_edges_from(edges)
	predict = {}
	while entitydic:
		value = 0
		key = ""
		pr = nx.pagerank(G)
		entitylist = entitydic.items()
		for k,v in entitylist:
			for canentity in v:
				entityvalue = pr[canentity]
				if entityvalue>value:
					value = entityvalue
					targetentity = canentity
					key = k
		predict[key] = canentity
		removelist = entitydic[key]
		removelist.remove(predict[key])
		G.remove_nodes_from(removelist)
		entitydic.pop(key)
	return predict

def getGraphByRandomWalk(edges,nodes):
	pass

def entitydic_split(targetlist,edges,nodes,split_len):
	pass


def main():
	starttime = dt.datetime.now()
	entitydoc,doccandidate,entitydicsvalue = getCandidate()
	print("entitydicsvalue=" + str(entitydicsvalue))
	# entitydoc,doccandidate = getCandidateByWiki()
	#print('entitydoc:'+ str(entitydoc))
	'''entitydoc:['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9']'''
	#print("doccandidate" + str(doccandidate))
	'''
	doccandidate{
	'1': [{'王健林': ['王健林（万达集团创办人兼董事长）']}, [['王健林', '王健林（万达集团创办人兼董事长）']]], 
	'10': [{'万达': ['大连万达集团股份有限公司']}, [['万达', '大连万达集团股份有限公司']]], 
	'11': [{'阿里': ['阿里巴巴集团', '桃花坞木版年画', '穆罕默德·阿里', '桑尼·阿里', '阿里巴巴公司', '阿里+(姓氏)', '阿里山山脉', '阿里山', '阿里山乡']}, [['阿里', '阿里巴巴集团']]], 
	'12': [{'阿里巴巴': ['阿里巴巴集团']}, [['阿里巴巴', '阿里巴巴集团']]], 
	'2': [{'电子商务': ['电子商务', '电子商务（电商平台）', '雷尼蕨', '家养化']}, [['电子商务', '电子商务（电商平台）']]], 
	'3': [{'电商': ['电子商务（电商平台）']}, [['电商', '电子商务（电商平台）']]], 
	'4': [{'马爸爸': ['马云（阿里巴巴集团创始人、亚洲首富）']}, [['马爸爸', '马云（阿里巴巴集团创始人、亚洲首富）']]], 
	'5': [{'马云': ['马云', '马云（阿里巴巴集团创始人、亚洲首富）']}, [['马云', '马云（阿里巴巴集团创始人、亚洲首富）']]], 
	'6': [{'腾讯': ['腾讯', '深圳市腾讯计算机系统有限公司', '伯句', '台中生活圈4号道路', '2006年香港国际七人榄球赛']}, [['腾讯', '深圳市腾讯计算机系统有限公司']]], 
	'7': [{'百度': ['百度', '百度（百度公司）', '2003年至2004年意大利甲组足球联赛']}, [['百度', '百度（百度公司）']]], 
	'8': [{'网络': ['网上邻居（互联网）', '生物神经网络', '计算机网络']}, [['网络', '网上邻居（互联网）']]], 
	'9': [{'苏宁': ['苏宁易购集团股份有限公司', '苏宁+(军人)', '苏宁+(银行家)', '苏宁电器', '苏宁环球']}, [['苏宁', '苏宁易购集团股份有限公司']]]} 
	'''
	print ("Candidate entity complete!")
	correctnumber = 0
	totalnumber = 0

	for doc in entitydoc:
		print (doc + ":")
		starttime0 = 0
		endtime0 = 0
		cn = 0
		tm = 0
		starttime0 = dt.datetime.now()
		entitydic,targetlist = doccandidate[doc]

		print("entitydic(候选实体为)==" + str(entitydic))

		entitypairarray = getEntityPair(entitydic,doccandidate)

		print("entitypairarray=" + str(entitypairarray))

		patharray = getPairArrayPath(entitypairarray)
		print("patharray=" + str(patharray))

		edges,nodes = getEdges(patharray)
		print("edges=" + str(edges))
		print("nodes=" + str(nodes))

		print ("edges:" + str(len(edges)))
		for m in entitydic.items():
			for n in m[1]:
				nodes.append(n)
		nodes = list(set(nodes))
		print ("nodes:" + str(len(nodes)))
		predict = getGraphByStandardPagelink(entitydic,edges,nodes)
		for mention,target in targetlist:
			totalnumber += 1
			tm += 1
			if predict[mention] == target:
				correctnumber += 1
				cn += 1
			print ("mention:" + mention + "   target:" + target + "     predict:" + predict[mention])
		endtime0 = dt.datetime.now()
		print ("doc_totalnumber:" + str(tm))
		print ("doc_correctnumber:" + str(cn))
		print ("doc_precious:" + str(float(cn)/tm))
		print ("doc_runtime:" + str(endtime0 - starttime0))
		print ("***************************************************")
	print ("totalnumber:" + str(totalnumber))
	print ("correctnumber:" + str(correctnumber))
	print ("precious:" + str(float(correctnumber)/totalnumber))
	endtime = dt.datetime.now()
	print ("runtime:" + str(endtime - starttime))

def main1():
	starttime = dt.datetime.now()
	entitydoc,doccandidate = getCandidate()
	# entitydoc,doccandidate = getCandidateByWiki()
	print ("Candidate entity complete!")
	correctnumber = 0
	totalnumber = 0
	for doc in entitydoc:
		print (doc + ":")
		starttime0 = 0
		endtime0 = 0
		cn = 0
		tm = 0
		starttime0 = dt.datetime.now()
		entitydic,targetlist = doccandidate[doc]
		entitypairarray = getEntityPair1(entitydic)
		patharray = getPairArrayPath1(entitypairarray)
		edges,nodes = getEdges(patharray)
		print ("edges:" + str(len(nodes)))
		for m in entitydic.items():
			for n in m[1]:
				nodes.append(n)
		nodes = list(set(nodes))
		print ("nodes:" + str(len(nodes)))
		predict = getGraphByStandardPagelink1(entitydic,edges,nodes)
		for mention,target in targetlist:
			totalnumber += 1
			tm += 1
			if predict[mention] == target:
				correctnumber += 1
				cn += 1
			print ("mention:" + mention + "   target:" + target + "     predict:" + predict[mention])
		endtime0 = dt.datetime.now()
		print ("doc_totalnumber:" + str(tm))
		print ("doc_correctnumber:" + str(cn))
		print ("doc_precious:" + str(float(cn)/tm))
		print ("doc_runtime:" + str(endtime0 - starttime0))
		print ("***************************************************")
	print ("totalnumber:" + str(totalnumber))
	print ("correctnumber:" + str(correctnumber))
	print ("precious:" + str(float(correctnumber)/totalnumber))
	endtime = dt.datetime.now()
	print ("runtime:" + str(endtime - starttime))

# def main2():
# 	starttime = dt.datetime.now()
# 	entitydoc,doccandidate = getCandidateByRule()
# 	# entitydoc,doccandidate = getCandidateByPriorRule()
# 	print ("Candidate entity complete!")
# 	correctnumber = 0
# 	totalnumber = 0
# 	prenullnumber = 0
# 	realnullnumber = 0
#
# 	for doc in entitydoc:
# 		print (doc + ":")
# 		starttime0 = 0
# 		endtime0 = 0
# 		cn = 0
# 		tm = 0
# 		starttime0 = dt.datetime.now()
# 		entitydic,targetlist = doccandidate[doc]
#
# 		if len(entitydic) == 1:
# 			totalnumber += 1
# 			tm += 1
# 			if entitydic[targetlist[0][0]] == []:
# 				prenullnumber += 1
# 			if targetlist[0][1] == "NULL":
# 				realnullnumber += 1
# 			if targetlist[0][1] == entitydic[targetlist[0][0]][0]:
# 				correctnumber += 1
# 				cn += 1
# 			print ("mention:" + targetlist[0][0] + "   target:" + targetlist[0][1] + "     predict:" + entitydic[targetlist[0][0]][0])
# 		else:
# 			entitypairarray = getEntityPair(entitydic)
# 			patharray = getPairArrayPath(entitypairarray)
# 			edges,nodes = getEdges(patharray)
# 			print ("edges:" + str(len(nodes)))
# 			for m in entitydic.items():
# 				for n in m[1]:
# 					nodes.append(n)
# 			nodes = list(set(nodes))
# 			print ("nodes:" + str(len(nodes)))
# 			predict = getGraphByStandardPagelink(entitydic,edges,nodes)
# 			for mention,target in targetlist:
# 				totalnumber += 1
# 				tm += 1
# 				if predict[mention] == "NULL":
# 					prenullnumber += 1
# 				if target == "NULL":
# 					realnullnumber += 1
# 				if predict[mention] == target:
# 					correctnumber += 1
# 					cn += 1
# 				print ("mention:" + mention + "   target:" + target + "     predict:" + predict[mention])
# 		endtime0 = dt.datetime.now()
# 		print ("doc_totalnumber:" + str(tm))
# 		print ("doc_correctnumber:" + str(cn))
# 		print ("doc_precious:" + str(float(cn)/tm))
# 		print ("doc_runtime:" + str(endtime0 - starttime0))
# 		print ("***************************************************")
# 	print ("totalnumber:" + str(totalnumber))
# 	print ("correctnumber:" + str(correctnumber))
# 	print ("prenullnumber:" + str(prenullnumber))
# 	print ("realnullnumber:" + str(realnullnumber))
# 	precious = float(correctnumber - prenullnumber)/(totalnumber - prenullnumber)
# 	recall = float(correctnumber - prenullnumber)/(totalnumber - realnullnumber)
# 	print ("precious:" + str(precious))
# 	print ("recall:" + str(precious))
# 	print ("F1:" + str((2*precious*recall)/(precious+recall)))
# 	endtime = dt.datetime.now()
# 	print ("runtime:" + str(endtime - starttime))



def test():
	#entitydoc,doccandidate = getCandidateByWiki()
	entitydoc,doccandidate = getCandidate()
	print ("Candidate entity complete!")

if __name__ == '__main__':
	main()
	#test()
	
	'''
	#print getMutiCanByEdit(['Michael_Jordan','Chicago_Bulls'],5)
	#print getCanByEdit("Gingrich",6)
	starttime = dt.datetime.now() 
	entitydoc,doccandidate = getCandidate()
	#doc = 'PROXY_XIN_ENG_20041010.0024'
	#doc = 'bolt-eng-DF-170-181103-8882382'
	doc = "PROXY_XIN_ENG_20041010.0024"
	entitydic,targetlist = doccandidate[doc]
	entitypairarray = getEntityPair1(entitydic)
	patharray = getPairArrayPath1(entitypairarray)
	#patharray = getPairArrayPath1(entitypairarray,3)
	edges,nodes = getEdges(patharray)
	print len(nodes)
	for m in entitydic.items():
		for n in m[1]:
			nodes.append(n)
	nodes = list(set(nodes))
	print len(nodes)
	predict = getGraphByStandardPagelink(entitydic,edges,nodes)
	#predict = getGraphByGreedSearch(entitydic,edges,nodes)
	print entitydic
	print targetlist
	print predict
	correctnumber = 0
	totalnumber = 0
	for mention,target in targetlist:
		totalnumber +=1
		if predict[mention] == target:
			correctnumber +=1
	print "totalnumber:" + str(totalnumber)
	print "correctnumber:" + str(correctnumber)
	print "precious:" + str(float(correctnumber)/totalnumber)
	endtime = dt.datetime.now()
	print "runtime:" + str(endtime - starttime)
	'''
