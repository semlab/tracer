import json


class Entity:

    def __init__(self):
        self.id = None
        self.name = None
        self.alt_name = None
        self.wikidata = None

class Company(Entity):

    def __init__(self):
        super().__init__()
        self.industry = None

class Person(Entity):

    def __init__(self):
        super().__init__()

class Place(Entity):

    def __init__(self):
        super().__init__()
    

class Relation:

    def __init__(self):
        self.source = None
        self.destination = None


class NodeType:
    ORG = "ORG"
    PERSON = "PERSON"
    PLACE = "GPE"
    Set = {"ORG", "PERSON", "GPE", "LOCATION"}
    #Set = [NodeType.ORG, NodeType.PERSON, NodeType.PLACE}"ORG", "PERSON", "GPE"]


class EdgeType:
    TRADE = "TRADE"
    OTHER = "OTHER"
    Set = ["TRADE", "OTHER"]


class Node:
    """
    ent_count is the number of time the entity was identify in the corpus
    """

    def __init__(self, label, ner_type, count=0):
        self.id = self.id_from_label(label)
        self.ner_type = ner_type
        self.label = label 
        self.count = count
        self.aliases = []


    def id_from_label(self, label=None):
        id_str = label if label is not None else self.label
        id_str = id_str.lower()
        if id_str.startswith("the "): 
            id_str = id_str[4:]
        elif id_str.startswith("an "):
            id_str = id_str[3:]
        # TODO is below necessary ? how to make it efficient ? chain .replace?
        id_str = id_str.replace("'s", "") 
        id_str = id_str.replace(".", "") 
        id_str = id_str.replace(",", "") 
        id_str = id_str.replace("(", "") 
        id_str = id_str.replace(")", "") 
        id_str = id_str.replace("<", "") 
        id_str = id_str.replace(">", "") 
        id_str = id_str.replace("\"", "") 
        id_str = id_str.replace("/", "-") 
        id_str = id_str.replace("'", "") 
        id_str = id_str.replace(" ", "-") 
        id_str = id_str.replace(" ", "") # remove all left spaces
        id_str = id_str.strip("- ")
        #TODO: remove multiple dashes
        return id_str

    @staticmethod
    def color(ent_type):
        if ent_type == 'PERSON': return 'red'
        elif ent_type == 'ORG': return 'blue'
        elif ent_type == 'GPE': return 'green'
        elif ent_type == 'LOCATION': return 'green'
        else: return 'gray'

    def __eq__(self, other):
        return self.id == other.id
    
    def __str__(self):
        return str(self.__dict__)



class Link:

    def __init__(self, source, target, rel_type=None, label=None, props={}):
        self.source = source
        self.target = target
        self.rel_type = rel_type
        self.labels = []
        if label is not None:
            self.labels.add(label)
        self.props = props


    def add_label(self, label):
        if label not in self.labels:
            self.labels.append(label)

    def __eq__(self, other):
        return self.source == other.source and self.target == other.target

    def __str__(self):
        return str(self.__dict__)



class NodeEncoder(json.JSONEncoder):

    def default(self, obj):
        if issinstance(obj, Node):
            return {
                'ent_id': obj.ent1_id,
                'ent_type': obj.ent_type,
                'ent_label': obj.ent_label
            }
        return json.JSONEncoder(self, obj)
