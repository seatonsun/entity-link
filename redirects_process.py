# coding=utf-8
from urllib import parse
import re

'''转码重定向文件'''



def main():
    global i
    global k
    a = {}
    infile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_redirects_zh.ttl", "r")
    outfile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_redirects_zh.txt", 'w', encoding='utf-8')
    k = 1
    i = 0
    line = str(infile.readline())
    while line:
        match = re.search("(<http://zhishi.me/zhwiki/resource/)(.*)(>)", str(line))
        if match and i < 2:
            a[i] = match.group(2)
            a[i] = parse.unquote(a[i])
            #a[i] = a
            i += 1
            line = str(infile.readline())
        elif match and i == 2:

            strtemp = a[0] + '\t' + a[1] + '\n'
            outfile.write(strtemp)
            a[1] = a[2] = None
            i = 0
            line = str(infile.readline())
            print(str(k) + strtemp)
            k += 1
        else:
            line = str(infile.readline())

if __name__ == '__main__':
    main()
    print("end")

    ''' a, b = line.strip('<http://dbpedia.org/resource/').strip('> .\n').split(
                '> <http://dbpedia.org/ontology/wikiPageWikiLink> <http://dbpedia.org/resource/')
            entity1 = urllib.unquote(a).decode('utf-8', 'ignore').encode('utf-8')
            entity2 = urllib.unquote(b).decode('utf-8', 'ignore').encode('utf-8')
    
            strtemp = entity1 + '\t' + entity2 + '\n'
            num += 1
            print(str(num) + ' ' + strtemp)
            outfile.write(strtemp)

            line = infile.readline()'''
