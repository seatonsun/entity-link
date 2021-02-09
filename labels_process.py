#coding=utf-8
#import urllib
from urllib import parse
import re
import urllib.request
#infile = open("/home/john/entitylink/dataset/labels_en.nt")
#outfile = open('/home/john/entitylink/dataset/labels_en.txt', 'w')
def main():
	infile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_labels_zh.ttl","rb")
	outfile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_labels_zh.txt", 'w',encoding='utf-8')
	line = infile.readline()
	num = 0
	while line:
		#match = re.search("(<http://zhishi.me/zhwiki/resource/)(.*)(> <http://www.w3.org/2000/01/rdf-schema#label>)",str(line))
		match = re.search("(<http://zhishi.me/zhwiki/resource/)(.*)(>)",str(line))
		if match:
			entity = match.group(2)
			#entity1 = urllib.unquote(entity).decode('utf-8','ignore').encode('utf-8')
			entity1 = parse.unquote(entity)

			print(entity1)
			strtemp = str(entity1) + '\t' + str(entity1) + '\n'
			outfile.write(strtemp)
			print (str(num) + ' ' + strtemp)
			num += 1
		line = infile.readline()

if __name__ == '__main__':
	main()
	print("end")