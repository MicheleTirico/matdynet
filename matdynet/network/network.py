import networkx as nx
import os

from matdynet.config import config
from matdynet.network.stateSet import StateSet
import lxml.etree as ET


class Network ():
    """ table variables
    G_shp   :   graph from he shp file
    G_sim   :   graph to use in simulation (to cast in xml)
    G_states:   simplified graph with states (to cast in xml)
    """

    # constructor
    def __init__(self, con):
        self.config = con
        self.sim = config.Simulation(self.config)
        self.urls = config.Urls(self.config)
        self.scenario =self.urls.getUrl("scenario")
        self.shp = self.config.getValWith2Attrib("urls","url",["name","type"],["network_shp","file"])
        self.city = os.path.splitext(self.shp)[0]
        self.urlShp = self.config.getAbsolutePath()+"/scenarios/"+self.urls.getUrl("scenario")+"/"+self.urls.getUrl("network_shp")
        self.urlXml = self.config.getAbsolutePath()+"/scenarios/"+self.urls.getUrl("scenario")+"/"+self.urls.getUrl("network") # for the sim
        self.urlNetwork=self.config.getAbsolutePath()+"/scenarios/"+self.urls.getUrl("scenario")+"/"+self.urls.getUrl("network")
        self.urlNetworkSim=self.config.getAbsolutePath()+"/"+self.urls.getUrl("url_output")+"/"+self.urls.getUrl("scenario")+"/"+self.urls.getUrl("networksim")
        self.urlNetworkToRemove=self.config.getAbsolutePath()+"/"+self.urls.getUrl("tmp")+"/netToRemove.xml"
    #    self.urlNetworkTmpXml=self.config.getAbsolutePath()+"/"+self.urls.getUrl("tmp")+"/networkXml.xml"

         # deprecated
        self.urlXmlStates = self.config.getAbsolutePath()+"/"+self.urls.getUrl("url_output")+"/"+self.urls.getUrl("scenario")+"/"+self.urls.getUrl("network_states")

        # init
        self.states = StateSet(self.config)
        self.__setupNetwork()

    def initStates(self):     self.states = StateSet(self.config)

    # setup
    def __setupNetwork (self):
        try:
            self.G_shp=nx.read_shp(self.urlShp)
            self.G_shp = nx.convert_node_labels_to_integers(self.G_shp, first_label=0, label_attribute = "coord")
        except RuntimeError: print("LOG: no graph from shapefile are fixed. Probably because we not need it")
        self.G_sim = nx.Graph()
        self.G_states = nx.Graph()

    def plotGraph(self):    nx.draw(self.G_shp)

    # get methods
    def getGraphShp(self):       return self.G_shp
    def getGraphSim(self):       return self.G_sim
    def getGraphStates(self):       return self.G_states

    # map states-network
    # ---------------------------------------------------------------------------------------
    def initMapLinks(self):
        self.__mapLinks={}
        print (self.config.urlNetworkTmp)
        tree_net=ET.parse(self.config.urlNetworkTmp)
        root_net=tree_net.getroot()
        links_net=root_net.findall("links")[0]
        for link in links_net:
            attributes=link.find("attributes")
            id_link_states=attributes.findall("./attribute[@name='"+"id_link_states"+"']")[0].text
            self.__mapLinks[int(link.attrib["id"])]=id_link_states

    def getMap(self):   return self.__mapLinks
    def updateMap(self,id_link):   self.__mapLinks[len(self.__mapLinks)+1]=id_link

    def setAttribute(self,root,name,val):
        try:                attributes=root[0]
        except IndexError:  attributes= ET.SubElement(root,"attributes",{})
        try:                attribute=attributes.findall("./attribute[@name='"+name+"']")[0]
        except:             attribute= ET.SubElement(attributes,"attribute",{"name":name,"class":"java.lang.String"})
        attribute.text=str(val)

    def setAttributeWithAttributes(self,attributes,name,val):
        try:                attribute=attributes.findall("./attribute[@name='"+name+"']")[0]
        except:             attribute= ET.SubElement(attributes,"attribute",{"name":name,"class":"java.lang.String"})
        attribute.text=str(val)

    def addHeaderAndStoreXml (self, root, toAdd,newf,pathTmp):
        tree= ET.ElementTree (root)
        tree.write(pathTmp,pretty_print = True)
        f = open(pathTmp,'r')
        newf = open(newf,'w')
        lines = f.readlines()
        newf.write(toAdd)
        for line in lines:  newf.write(line)
        newf.close()
        f.close()
        os.remove(self.urlNetworkToRemove)

    def test (self,a):    print (a)