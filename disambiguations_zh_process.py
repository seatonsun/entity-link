import re
from urllib import parse

'''做的是disambigusations_zh.ttl文件的预处理'''


def main():
    global i
    global k
    a = {}
    k = 1
    i = 0
    parttern = r','
    infile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_disambiguations_zh.ttl", "rb")
    outfile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_disambiguations_zh_new.txt", 'w', encoding='utf-8')
    line = infile.readline()

    while line and k < 11252:
            match = re.search("(<http://zhishi.me/zhwiki/resource/)(.*)(>)", str(line))
            if match and i == 0:
                a[i] = match.group(2)
                a[i] = parse.unquote(a[i])
                # a[i] = a
                i += 1
                line = str(infile.readline())
            elif match and i == 1:
                strtemp1 = None
                # match1 = re.split("[,|.|?|!]", str(line))

                match1 = parse.unquote(str(line))
                match1 = match1.split(',')
                print(match1)

                for l in match1:
                    fina = re.search("(<http://zhishi.me/zhwiki/resource/)(.*)(>)", str(l))
                    if fina:
                        littleFina = fina.group(2)
                        strtemp = a[0] + '\t' + littleFina + '\n'
                        outfile.write(strtemp)
                        #
                        # if strtemp1 ==None:
                        #     strtemp1 = str(littleFina) + '\t'
                        # else:
                        #     strtemp1 = str(strtemp1) + str(littleFina) + '\t'
                # strtemp = a[0] + '\t' + strtemp1 + '\n'
                #outfile.write(strtemp)
                a[0] = a[1] = a[2] = None
                i = 0
                line = str(infile.readline())
                print(str(k))
                k += 1
            else:
                line = str(infile.readline())


def test():
    infile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_disambiguations_zh.ttl", "rb")
    outfile = open(r"C:\Users\dell\Desktop\实体链接任务的数据\2.0_zhwiki_disambiguations_zh1.txt", 'w', encoding='utf-8')
    line = infile.readline()
    while line:
        entity1 = parse.unquote(str(line))
        entity1 = entity1 + '\n'
        outfile.write(entity1)
        print(entity1)
        line = infile.readline()


if __name__ == '__main__':
    #test()
    main()
    print("end")
