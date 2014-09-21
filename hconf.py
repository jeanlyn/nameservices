#!/usr/bin/env python
#encoding=utf-8
from xml.etree.ElementTree import Element 
from xml.etree import ElementTree
from xml.dom import minidom
import os
class HadoopConf():
    def __init__(self,fileName):
        self.filename=fileName
        self.TagName="configuration"
        self.dt={}
        #判断XML是否存在
        if os.path.isfile(self.filename) == True:
            #print "the xml has load"
            self.tree=ElementTree.parse(self.filename)
        else:
            #print "The file is not exist,please cheack the path!and the program is create the file!"
            self.createRootTag(self.TagName)
            #print "the file have been successfully created!"
            self.tree=ElementTree.parse(self.filename)
        self.root=self.tree.getroot()

    def createRootTag(self,name):
        self.fileContent="<"+name+">"+"</"+name+">"
        xmlfile=file(self.filename,'w')
        xmlfile.write(self.fileContent)
        xmlfile.close()
        return

    #返回一个字典形式：{'file.replication': {'description': '', 'value': '1'}, 'fs.defaultFS': {'description': 'In case you do not want to use the default scheduler', 'value': 'hdfs://jeanlyn:9000'}}
    def get(self):
        element=self.tree.findall('property')
        #for k,v in [(a.getchildren()[0].text,a.getchildren()[1].text) for a in element]:
        for a in element:
            k=a.find("name").text
            vn=a.find("value")
            v= vn.text if vn is not None else ""
            dn=a.find("description")
            d= dn.text if dn is not None else ""
            final=a.find("final")
            #print k,v
            self.dt[k]={"value":v,"description":d}
        return self.dt

    #modify the key 
    def set(self,key,value1):
        self.dt[key]=value1
        name=Element("name")
        name.text=str(key)
        value=Element("value")
        value.text=str(value1)
        proper=Element("property")
        proper.append(name)
        proper.append(value)
        self.root.append(proper)
        self.tree.write(self.filename)
    
    #将字典保存为xml文件
    def setdt(self,tree):
        self.dt=tree
        self.tree=ElementTree.ElementTree(Element(self.TagName,{}))
        sroot=self.tree.getroot()
        #print sroot
        for k,v in zip(tree.keys(),tree.values()):
            name=Element("name")
            name.text=str(k)
            value=Element("value")
            value.text=str(v['value'])
            description=Element("description")
            description.text=str(v['description'])
            proper=Element("property")
            proper.append(name)
            if value.text!= '':
                proper.append(value)
            if description.text!='':
                proper.append(description)
            sroot.append(proper)
        #self.tree.write(self.filename)
        with open(self.filename,'w') as f:
            f.write(self.prettify(sroot))

    def prettify(self,elem):
        rough = ElementTree.tostring(elem,'utf-8')
        reparsed = minidom.parseString(rough)
        return reparsed.toprettyxml(indent="    ")

if __name__ =="__main__":
    tree=HadoopConf("core-site.xml")
    dt=tree.get()
    #dt["123"]={"value":"dsaf","description":"dsad"}
    #tree.setdt(dt)
       
    print dt