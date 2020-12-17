import argparse
import datetime
import os
import re

def mode2num(Mode):
    if Mode == "easy":
        return 1
    elif Mode == "normal":
        return 2
    elif Mode == "hard":
        return 3
    else:
        exit("[-] Error in function mode2num")

def saveDics(path,dics):
    dics = list(set(dics))
    fp = open(path,"w+",encoding="utf-8")
    fp.writelines(dics)
    fp.close()
    size = str(int(os.path.getsize(path)/1024))
    print("[+]字典已生成,条目:{num}条,大小:{size} kb".format(num=len(dics),size=size))

def loadElementFile(Type,Mode):
    base_path = "element/"
    files = []
    Element = {}
    #获取所有相关的子元素文件
    for fn in os.listdir("element"):
        if re.match("^"+Type+"\.\w+\.txt",fn) or re.match("^"+Type+"\.txt",fn) or re.match("^element\.\w+\.txt",fn):
            files.append(base_path+fn)
    try:
        for fn in files:
            cname = ""
            cmode = ""
            fp = open(fn,"r",encoding="utf-8")
            content = fp.readlines()
            fp.close()
            if len(fn.split(".")) == 3:
                cname = fn.split(".")[1]
            for n in content:
                if re.match("\s",n) or re.match("^\s?#",n) :
                    continue
                #当文件为type.txt
                elif len(fn.split(".")) == 2 and re.match("^\s?\[(\w+)\.(\w+)\]\s?",n):
                    conf = re.match("^\s?\[(\w+)\.(\w+)\]\s?",n)
                    cname = conf.group(1)
                    cmode = mode2num(conf.group(2))
                    if not (cname in Element.keys()):
                        Element[cname] = []
                #当文件为type.Mode.txt
                elif len(fn.split(".")) == 3 and re.match("^\s?\[(\w+)\]\s?",n):
                    conf = re.match("^\s?\[(\w+)\]\s?",n)
                    cmode = mode2num(conf.group(1))
                    if not (cname in Element.keys()):
                        Element[cname] = []
                elif cname != "" and cmode <= Mode:
                    Element[cname].append(n.strip())
    except Exception as e:
        exit('[-]读取元素文件过程中出错！请检查元素文件内容的格式')
    #去重和去除空元素集
    null_Element_keys = []
    for key in Element.keys():
        if len(Element[key]) == 0:
            null_Element_keys.append(key)
        else:
            Element[key] = list(set(Element[key]))
    for nk in null_Element_keys:
        Element.pop(nk)
    return Element

def loadRuleFile(Mode,Rulefile):
    Rulelist = []
    flag = 0
    if len(Rulefile.split(",")) >= 2:
        a = [loadRuleFile(Mode,m) for m in Rulefile.split(",")]
        for a1 in a:
            Rulelist = Rulelist + a1
        return Rulelist
    else:
        fp = open("rule/"+Rulefile+".rule", "r",encoding="utf-8")
        content = fp.readlines()
        fp.close()
        for n in content:
            #跳过注释
            if re.match("\s",n) or re.match("^\s?#",n) :
                continue
            elif re.match("^\s?\[(\w+)\]\s?",n):
                conf = re.match("^\s?\[(\w+)\]\s?",n)
                cmode = mode2num(conf.group(1))
                if cmode <= Mode:
                    flag = 1
                else:
                    flag = 0
            elif flag == 1:
                Rulelist.append(n.strip()+"\n")
        #去重
        Rulelist = list(set(Rulelist))
        return Rulelist

def filter(Filter,Dics):
    nDics = []
    if Filter != None:
        for n in Dics:
            if re.match(Filter,n):
                continue
            else:
                nDics.append(n)
        return nDics
    else:
        return Dics
class RuleParser:
    def __init__(self,rule):
        self.rule = rule
        self.element = {}
    def ElementParser(self,Element):
        self.element = Element
        remove_rule = []
        self.no_element_Dics = []
        all_keys = {}
        for r in self.rule:
            remove_rule_flag = 0
            #提取所有规则中不同keys的组合方式作为索引
            keys = re.findall("\$(.+?)\$",r)
            if keys != None and len(keys) >= 1:
                #当具体key的element为空时，跳过该索引，废弃该规则
                for k in keys:
                    if k not in self.element.keys():
                        remove_rule.append(r)
                        remove_rule_flag = 1
                        print("[-]无效规则: {rule},变量${key}$没有被定义".format(rule=r.strip(),key=k))
                        break
                if remove_rule_flag == 1:
                    continue
                keys.sort()
                keys = tuple(keys)
                if keys not in all_keys.keys():
                    all_keys[tuple(keys)] = {}
        for r in remove_rule:
            self.rule.remove(r)
        #根据不同的键值，生成对应键值的排列组合元素表
        for keys in all_keys.keys():
            key_element_list = []
            for key in keys:
                key_element_list.append(self.element[key])
            all_keys[keys] = self.Permutaions(key_element_list)
        #重新读取规则，把具体元素代入规则中生成字典
        for r in self.rule:
            ks = re.findall("\$(.+?)\$",r)
            if ks != None and len(ks) >= 1:
                index = {}
                mks = ks
                ks.sort()
                for k in mks:
                    index[k] = ks.index(k)
                for s in all_keys[tuple(ks)]:
                    template = r
                    for key in ks:
                        template = template.replace("$"+key+"$",s[index[key]])
                    self.no_element_Dics.append(template)
        return self.no_element_Dics

    def Permutaions(self,elements):
        if len(elements) == 2:
            new = []
            for e1 in elements[0]:
                for e2 in elements[1]:
                    if type(e1) == str:
                        e1 = [e1]
                    if type(e2) == str:
                        e2 = [e2]
                    new.append(e1+e2)
            return new
        elif len(elements) <= 1:
            return [ [n] for n in elements[0] ]
            #return elements
        else:
            left = elements.pop(0)
            right = self.Permutaions(elements)
            new = [left,right]
            return self.Permutaions(new)

class loadDynamicElement:
    def __init__(self,Type,Mode,Rule):
        self.Mode = Mode
        self.rule = Rule
        self.DynamicElement = {}
        self.all_keys = []
        for r in self.rule:
            keys = re.findall("\$(.+?)\$",r)
            self.all_keys = self.all_keys + keys
        self.all_keys = list(set(self.all_keys))
        self.createDomainElement()
        self.createTimeElement()
    def createDomainElement(self):
        if Domain == None:
            return False
        DomainFormat = len(Domain.split("."))
        Domainkey = ["D:.","D:_","D:","D::","D:-"]
        print(DomainFormat)
        if DomainFormat != 2 and DomainFormat != 3:
            exit("[-]请输入正确的域名格式，如example.com or sub.example.com")
        #定义域名的几种组合方式
        if DomainFormat == 2:
            element = {"main":[Domain.split(".")[0]],"ext":[Domain.split(".")[1]]}
            DomainElementRule = {
                "D:":["$main$"],
                "D:_":['$main$_$ext$'],
                "D:.":["$main$.$ext$"],
                "D:-":["$main$-$ext$"],
                "D::": ["$main$.$ext$","$main$_$ext$","$main$","$main$-$ext$"],
            }
        if DomainFormat == 3:
            element = {"sub":[Domain.split(".")[0]],"main":[Domain.split(".")[1]],"ext":[Domain.split(".")[2]]}
            DomainElementRule = {
                "D:": ["$sub$","$main$"],
                "D:_": ["$sub$_$main$",'$main$_$ext$',"$sub$_$main$_$ext$"],
                "D:-": ["$sub$-$main$",'$main$-$ext$',"$sub$-$main$-$ext$"],
                "D:.": ["$sub$.$main$",'$main$.$ext$',"$sub$.$main$.$ext$"],
                "D::": ["$main$.$ext$", "$main$_$ext$", "$main$", "$sub$","$sub$_$main$","$sub$_$main$_$ext$","$sub$.$main$.$ext$","$sub$-$main$",'$main$-$ext$',"$sub$-$main$-$ext$"],
            }
        new_element = {}
        for k in Domainkey:
            new = {k:RuleParser(DomainElementRule[k]).ElementParser(element)}
            new_element = dict(new_element,**new)
#        new_element = {"DOMAIN":RuleParser(DomainElementRule).ElementParser(element)}
        self.DynamicElement = dict(self.DynamicElement,**new_element)
        return True
    def createTimeElement(self):
        def dateRange(beginDate, endDate):
            dates = []
            dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
            #dt = datetime.datetime.strptime(beginDate, "%m-%d")
            date = beginDate[:]
            while date <= endDate:
                dates.append(date)
                dt = dt + datetime.timedelta(1)
                date = dt.strftime("%Y-%m-%d")
            return dates

        time_key = []
        new_element = {}
        #判断是否存在T变量
        for n in self.all_keys:
            ma = re.search("T:(\d+-\d+-\d+),(\d+-\d+-\d+):.*",n)
            if ma != None:
                time_key.append(n)
        #不存在直接退出方法
        if len(time_key) <= 0:
            return False
        #存在
        for n in time_key:
            self.DynamicElement[n] = []
            ma = re.search("^T:(\d+-\d+-\d+),(\d+-\d+-\d+):(.*)$",n)
            starttime,endtime = ma.group(1),ma.group(2)
            time_split = ma.group(3)
            template = dateRange(starttime,endtime)
            element = []
            if time_split == "":
                #YMD格式
                element = element + [ n.replace("-","") for n in template ]
                #sYMD格式
                element = element + [ n[2:].replace("-","") for n in template ]
                #YM格式
                element = element + [ n.split("-",1)[1].replace("-","") for n in template ]
                #sYM格式
                element = element + [ n.rsplit("-",1)[0][2:].replace("-","") for n in template ]
                #MD格式
                element = element + [ n.split("-",1)[1].replace("-","") for n in template ]
            else:
                #Y-M-D格式
                element = element + template
                #sY-M-D格式
                element = element + [ n[2:] for n in template ]
                #Y-sM-sD格式
                element = element + [ n.split("-")[0]+"-"+n.split("-")[1].replace("0","")+"-"+n.split("-")[2].replace("0","") for n in template ]
                #sY-sM-sD格式
                element = element + [ n.split("-")[0][2:]+"-"+n.split("-")[1].replace("0","")+"-"+n.split("-")[2].replace("0","") for n in template ]
                #Y-M格式
                element = element + [ n.rsplit("-",1)[0] for n in template ]
                #Y-sM格式
                element = element + [ n.split("-")[0]+"-"+n.split("-")[1].replace("0","") for n in template ]
                #sY-M格式
                element = element + [ n.split("-")[0][2:]+"-"+n.split("-")[1] for n in template ]
                #sY-sM格式
                element = element + [ n.split("-")[0][2:]+"-"+n.split("-")[1].replace("0","") for n in template ]
                #M-D格式
                element = element + [ n.split("-",1)[1] for n in template ]
                #sM-sD格式
                element = element + [ n.split("-")[1].replace("0","")+"-"+n.split("-")[2].replace("0","") for n in template ]
            element = list(set(element))
            if time_split != "-":
                element = [ n.replace("-",time_split) for n in element ]
            self.DynamicElement[n] = element
        return True
    def getDynamicElement(self):
        return self.DynamicElement

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m",dest="Mode",help="Easy,normal,hard",choices=['easy','normal','hard'],required=1)
    parser.add_argument("-D",dest="Domain",help="Domain")
    parser.add_argument("-f",dest="Filter",help="Filter")
    parser.add_argument("-S",dest="S",help="String:name,nickname,etc")
    parser.add_argument("-N",dest="N",help="Number:birthday,qq,phone number,etc")
    parser.add_argument("-r",dest="Rulefile",help="Rule file to load",required=1)
    parser.add_argument("-o",dest="Savepath",help="Output filename",required=1)
    args = parser.parse_args()
    Mode = mode2num(args.Mode)
    Savepath = args.Savepath
    Domain = args.Domain
    Filter = args.Filter
    Rulefile = args.Rulefile
    Type = Rulefile
    print("[*]加载规则文件",Rulefile)
    print("[*]选择模式为:",args.Mode)
    #初始化，读取规则和元素集
    Rule = loadRuleFile(Mode,Rulefile)
    Elements = loadElementFile(Type,Mode)
    if args.S != None:
        S = args.S
        Elements["S"] = S.strip(",").split(",")
    if args.N != None:
        N = args.N
        Elements["N"] = N.strip(",").split(",")
    DynamicElement = loadDynamicElement(Type,Mode,Rule)
    dynamicElement = DynamicElement.getDynamicElement()
    Elements = dict(Elements,**dynamicElement)
    ruleparser = RuleParser(Rule)
    print(Elements.keys())
    print('[*]字典生成中...')
    Dics = ruleparser.ElementParser(Elements)
    Dics = filter(Filter,Dics)
    saveDics(Savepath,Dics)
