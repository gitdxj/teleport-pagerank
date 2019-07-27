import os

DEFAULT_DIR = "pageLink/"

def readData(filename = "WikiData.txt"):
    '''
    filename: 数据文件名，默认取"WikiData.txt"
    return: 返回字典，key为NodeID，value为一个list，其中的元素为所有该key所指向的NodeID
    '''
    link_dict = dict()
    file = open(filename, 'r')
    lines = file.readlines()
    for each_line in lines:
        #print(each_line)
        page_list = each_line.strip().split()
        fromNodeID = int(page_list[0])
        toNodeID = int(page_list[1])
        #print("fromNodeID :" + str(fromNodeID) + '\n' + "toNodeID :" + str(toNodeID) )
        if fromNodeID not in link_dict:
            link_dict[fromNodeID] = list()
        link_dict[fromNodeID].append(toNodeID)
    return link_dict


def readDataReversed(filename = "WikiData.txt"):
    '''
    filename: 数据文件名，默认取"WikiData.txt"
    return: 返回字典，key为NodeID，value为一个list，其中的元素为所有指向该key的节点
    '''
    link_dict = dict()
    file = open(filename, 'r')
    lines = file.readlines()
    for each_line in lines:
        #print(each_line)
        page_list = each_line.strip().split()
        fromNodeID = int(page_list[0])
        toNodeID = int(page_list[1])
        #print("fromNodeID :" + str(fromNodeID) + '\n' + "toNodeID :" + str(toNodeID) )
        if toNodeID not in link_dict:
            link_dict[toNodeID] = list()
        link_dict[toNodeID].append(fromNodeID)
    return link_dict


def readAllPage(filename = "WikiData.txt"):
    '''
    读取数据文件，返回所有页面ID的list
    '''
    page_list = list()
    file = open(filename, 'r')
    lines = file.readlines()
    for each_line in lines:
        #print(each_line)
        line_list = each_line.strip().split()
        fromNodeID = int(line_list[0])
        toNodeID = int(line_list[1])
        #print("fromNodeID :" + str(fromNodeID) + '\n' + "toNodeID :" + str(toNodeID) )
        if fromNodeID not in page_list:
            page_list.append(fromNodeID)
        if toNodeID not in page_list:
            page_list.append(toNodeID)
        page_list.sort()
    return page_list


def deadEnds(link_dict, pagelist):
    '''
    返回所有dead end构成的列表
    dead end是只有入度没有出度的页面
    '''
    dead_end_list = list()
    for each_page in pagelist:
        if each_page not in link_dict:
            dead_end_list.append(each_page)
    return dead_end_list


def wirtePageLink(srcID, dest_list):
    '''
    将对应的源页和其指向的目的页写入一个文件中保存
    文件名为:  $srcID.txt
    文件中内容为：srcID|outDegree: dest1, dest2, ... , destn
    '''
    if not os.path.exists(DEFAULT_DIR):
            os.mkdir(DEFAULT_DIR)
    filename = DEFAULT_DIR + str(srcID) + ".txt"
    out_degree = len(dest_list)
    string = str(srcID) + "|" + str(out_degree) + ":"
    for each_dest in dest_list:
        string += " " + str(each_dest)
    outFile = open(filename, 'w+')
    outFile.write(string)
    

def readPageLink(srcID):
    '''
    读取pageLink文件里的链接数据
    返回出度和其指向的页面list
    '''
    filename = DEFAULT_DIR + str(srcID) + ".txt"
    InFile = open(filename, 'r')
    string = InFile.read()
    p1 = string.find('|')  # 找到 '|' 的位置
    p2 = string.find(':')  # 找到
    str_src = string[0:p1]
    str_out_degree = string[p1+1:p2]
    str_dest_list = string[p2+1:]
    src = int(str_src)
    out_degree = int(str_out_degree)
    dest_list = [int(str_dest) for str_dest in str_dest_list.strip().split()]
    return out_degree, dest_list


def writeData(filename = "WikiData.txt"):
    '''
    从原始数据文件中读取数据，构建稀疏矩阵
    分块写入pageLink中
    '''
    file = open(filename, 'r')
    lines = file.readlines()
    for each_line in lines:
        #print(each_line)
        page_list = each_line.strip().split()
        fromNodeID = int(page_list[0])
        toNodeID = int(page_list[1])
        #print("fromNodeID :" + str(fromNodeID) + '\n' + "toNodeID :" + str(toNodeID) )
        filenamem = DEFAULT_DIR + str(fromNodeID) + ".txt"
        if not os.path.exists(filenamem):  # 若之前没有该文件
            dest_list = [toNodeID]
            wirtePageLink(fromNodeID, dest_list)
        else:  # 若之前就有该文件，则在后面补充上新的destination
            out_degree, dest_list = readPageLink(fromNodeID)
            if toNodeID not in dest_list:
                dest_list.append(toNodeID)
            wirtePageLink(fromNodeID, dest_list)


def writeRank(rank_new):
    '''
    把rank值写入磁盘中
    '''
    RANK_DIR = "rank/"
    if not os.path.exists(RANK_DIR):
        os.mkdir(RANK_DIR)
    for each_page in rank_new:
        r_value = rank_new[each_page]
        filename = RANK_DIR + str(each_page) + ".txt"
        file = open(filename, 'w+')
        file.write(str(r_value))


def rankInit(pagelist):
    '''
    把各页面rank值初始化为1/N
    '''
    RANK_DIR = "rank/"
    if not os.path.exists(RANK_DIR):
        os.mkdir(RANK_DIR)
    n_pages = len(pagelist)
    for each_page in pagelist:
        r_value = 1 / n_pages
        filename = RANK_DIR + str(each_page) + ".txt"
        file = open(filename, 'w+')
        file.write(str(r_value))


def readRank(pageID):
    '''
    从磁盘中读取rank值
    '''
    RANK_DIR = "rank/"
    filename = RANK_DIR + str(pageID) + ".txt"
    if not os.path.exists(filename):
        print("无此文件")
        return None
    file = open(filename)
    r_value = float(file.read())
    return r_value



def pagerank(link_dict, pagelist, dead_end_list, beta = 0.85):
    n_pages = len(pagelist)  # 页面总数
    r_old = dict()
    r_new = dict()
    for each_page in pagelist:
        r_old[each_page] = 1/n_pages
    convergence = False
    while not convergence:
        dead_end_sum = 0.0
        for each_end in dead_end_list:
            dead_end_sum += beta * r_old[each_end] / n_pages
        # dead_end_sum -= beta * r_old[each_end] / n_pages
        # 初始化 r_new
        for each_page in pagelist:
            r_new[each_page] = (1 - beta) / n_pages + dead_end_sum
        for src in link_dict:
            dest_list = link_dict[src]
            src_out_degree = len(dest_list)
            for each_dest in dest_list:
                r_new[each_dest] += beta * r_old[src] / src_out_degree

        sum = 0
        for i in pagelist:
            sum += r_new[i]
        print("本次迭代总和为："+ str(sum))
        
        err = 0
        threshold = 0.0001
        for each_page in pagelist:
            err += abs(r_old[each_page] - r_new[each_page])
        for each_page in pagelist:
            r_old[each_page] = r_new[each_page]
        convergence = err < threshold
    return r_new

def pagerank_test(link_dict, pagelist, dead_end_list, beta = 0.85):
    n_pages = len(pagelist)  # 页面总数
    r_old = dict()
    r_new = dict()
    for each_page in pagelist:
        r_old[each_page] = 1/n_pages
    convergence = False
    while not convergence:
        # 初始化 r_new
        for each_page in pagelist:
            r_new[each_page] = (1 - beta) / n_pages
        for src in link_dict:
            dest_list = link_dict[src]
            src_out_degree = len(dest_list)
            for each_dest in dest_list:
                r_new[each_dest] += beta * r_old[src] / src_out_degree

        sum = 0
        for i in pagelist:
            sum += r_new[i]
        print("本次迭代总和为："+ str(sum))
        
        err = 0
        threshold = 0.00000000000001
        for each_page in pagelist:
            err += abs(r_old[each_page] - r_new[each_page])
        for each_page in pagelist:
            r_old[each_page] = r_new[each_page]
        convergence = err < threshold
    return r_new
        


def pagerank_block(pagelist, dead_end_list, beta = 0.85):
    rankInit(pagelist)
    n_pages = len(pagelist)  # 页面总数
    pages_with_out_degree = [page for page in pagelist if page not in dead_end_list]  # 有出度的页面列表 
    r_new = dict()
    convergence = False
    while not convergence:
        dead_end_sum = 0.0
        for each_end in dead_end_list:
            dead_end_sum += beta * readRank(each_end) / n_pages
        # 初始化 r_new
        for each_page in pagelist:
            r_new[each_page] = (1 - beta) / n_pages + dead_end_sum
        for src in pages_with_out_degree:
            out_dgree, dest_list = readPageLink(src)
            for each_dest in dest_list:
                r_new[each_dest] += beta * readRank(src) / out_dgree

        sum = 0
        for i in pagelist:
            sum += r_new[i]
        print("本次迭代总和为："+ str(sum))

        err = 0
        threshold = 0.00000000000001
        for each_page in pagelist:
            err += abs(readRank(each_page) - r_new[each_page])

        writeRank(r_new)

        convergence = err < threshold
    return r_new


if __name__ == "__main__":
    pages = readAllPage()
    links = readData()
    deadends = deadEnds(links, pages)
    ranks = pagerank(links, pages, deadends)
    top_100 = sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:100]
    with open('result.txt', 'w') as f:
        for e in top_100:
            f.write(str(e[0]) + '\t' + str(e[1]) + '\n')