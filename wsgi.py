from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import math,numpy
from urlparse import urlparse

class Root:
    def __init__(self):
        self.partition=[]
        self.value=None
        self.attribute=None
        self.nodes=[]
        self.branch=None
    def __str__(self, level=0):
        s=""
        if(level!=0):
            s = "\t" * level + repr(self.branch) + ":\n"
            level+=1
        if self.value==None:
            ret = s+"\t" * level + repr(self.attribute) + "\n"
        else:
            ret = s+"\t" * level + repr(self.value) + "\n"
        for child in self.nodes:
            ret += child.__str__(level + 1)
        return ret

instances = []
dict_ml = {}

def entropy(variable):
    s=.0
    for i in variable:
        if(i!=0):
            s+=i*math.log(i,2)
    return -s


def informationGain(ex,exy,examples):
    s=.0
    for i in exy:
       s+=(i[2]/examples)*entropy(i[:2])
    return entropy(ex)-s

def count_partitions(instances,dict_ml):
    for i in dict_ml.keys():
        dict_ml[i]=0
    for instance in instances:
        if (instance[n] not in dict_ml.keys()):
            dict_ml[instance[n]] = 0
        dict_ml[instance[n]] += 1

def initialize(instances):
    c=0
    with open("input.txt","r") as f:
        instance=True
        while instance:
            c+=1
            instance=f.readline().strip().split(",")
            if(len(instance)==1):
                break
            instances.append(instance)


def get_best_attribute(instances,attributes,root_partition):
    maxgain=0
    maxgainattribute=0
    dict_ml={}
    count_partitions(instances,dict_ml)
    for i in attributes:
        partition=[]
        for j in set([el[i] for el in instances]):
            tempdict=dict(dict_ml)
            tempinstances = [instance for instance in instances if instance[i]==j]
            count_partitions(tempinstances, tempdict)
            partition+=[[tempdict[el]/(len(tempinstances)*1.0) for el in tempdict.keys()]+[len(tempinstances)]]#,[k for k in tempdict[n]]


        s=sum(root_partition[0])*1.0
        gain=informationGain(numpy.array(root_partition[0])/s,partition,s)
        if(maxgain<gain):
            maxgain=gain
            maxgainattribute=i

    return maxgainattribute


def build_tree(root,instances,dict_ml,attributes):
    root.partition=[[dict_ml[i] for i in dict_ml],[i for i in dict_ml]]
    n=len(instances)
    for k in root.partition[0]:
        if k==n:
          root.value=root.partition[1][root.partition[0].index(k)]
          return


    a=get_best_attribute(list(instances),attributes,root.partition)
    root.attribute=a
    for i in set([instance[a] for instance in instances]):
        newroot=Root()
        newroot.branch=i
        root.nodes.append(newroot)
        tempdict=dict(dict_ml)
        newinstances=[instance for instance in instances if instance[a]==i]
        count_partitions(newinstances,tempdict)
        tempattributes=list(attributes)
        tempattributes.remove(a)
        build_tree(newroot,newinstances,tempdict,tempattributes)


#########################Test Instances#################################
def test(root):

    with open("test.txt","r") as f:
        instance=True
        while instance:
            instance=f.readline().strip().split(",")
            nod = root
            if len(instance)==1:
                break
            while nod.value == None:
                if not nod.nodes:
                    break
                for i in nod.nodes:
                    if (nod.attribute != None and instance[nod.attribute] == i.branch):
                        nod = i
                if nod == root:
                    break

            print instance + ["Value: "+nod.value]




#########################Main APP#######################################

def main():
    global n
    initialize(instances)
    count_partitions(instances,dict_ml)
    root=Root()
    if instances:
        n=len(instances[0])-1
        build_tree(root,list(instances),dict(dict_ml),[i for i in range(n)])
    print root

    print "Testing TIME"

    test(root)
    return "OK"

n=0

##############################################

class ID3Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        query_components=[]
        if len(query) >1:
            query_components = dict(qc.split("=") for qc in query.split("&"))
        if "entropy" in query_components:
            imsi = query_components["entropy"]
            output="{\"entropy\":"+str(entropy(eval(imsi)))+"}"
        elif "gain" in query_components:
            imsi = query_components["gain"]
            imsi = imsi.split(";")
            print imsi
            output="{\"gain\":"+str(informationGain(eval(imsi[0]),eval(imsi[1]),eval(imsi[2])))+"}"
        elif "id3" in query_components:
            imsi = query_components["id3"]
            output="{\"id3\":"+main()+"}"
        else:
            imsi=""
            output="Invalid Command"
        print imsi
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(output)



def run():
    print('http server is starting...')

    # ip and port of server
    # by default http server port is 80
    server_address = ('54.173.248.172', 6969)
    httpd = HTTPServer(server_address, ID3Handler)
    print('http server is running...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()