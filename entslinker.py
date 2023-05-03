#!/usr/bin/python3

import argparse
import os
import json
import pandas as pd

        


class EntityLinker:

    def __init__(self, dataframe):
        """ dataframe from triplex"""
        self.dataframe = dataframe
        self.links = set() 
        self.lookup = dict()
        pass


    def find_links(self, keep_line=True):
        """list entities links from a dataframe from triplex
           keep_line: whether to remove the line representing a link
        """
        links = set()
        pronouns = ["he", "she", "it", "they"]
        for idx, row in df.iterrows():
            subj = row['SUBJECT']
            obj = row['OBJECT']
            rel = row['RELATION']
            not_pronouns = subj not in pronouns and obj not in pronouns
            same_entity_type = (row['SUBJ_ENT_TYPE'] == row['OBJ_ENT_TYPE']) 
            entities_only = (row['SUBJECT'] == row['SUBJ_ENT'] and row['OBJECT'] == row['OBJ_ENT'])
            if (rel == 'be' and same_entity_type and 
                    entities_only and not_pronouns
                    and 'Ltd' not in (subj, obj)): #extra manual fix reuter
                links.add((subj, obj))
                if not keep_line:
                    self.dataframe.drop(idx, inplace=True) # removing the line
        self.links = links
        return self.links


    def build_lookup(self):
        # TODO
        pass


    


# TODO delete
def entcount(df):#, entlinks=None):
    """
    returns a dictionary with the count of different entities
    """
    entcount = {}
    for idx, row in df.iterrows():
        subj_ent, obj_ent = row['SUBJ_ENT'], row['OBJ_ENT']
        '''
        if entlinks is not None:
            if subj_ent in entlinks:
                subj_ent = entlinks[subjent]
            if obj_ent in entlinks:
                obj_ent = entlinks[obj_ent]
        '''
        if subj_ent in entcount:
            entcount[subj_ent] += 1
        else:
            entcount[subj_ent] = 1
        if obj_ent in entcount:
            entcount[obj_ent] += 1
        else:
            entcount[obj_ent] = 1
    return entcount
        


#TODO elsewhere
def remove_contractions():
    pass
    
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, 
            help="input triples csv file")
    parser.add_argument('-o', '--output', required=True, 
            help="output with entity links filtered csv")
    parser.add_argument('-l', '--save-links', required=False,
            help="save the identified links")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['save-links'] = args.save_links
    return args_dict



if __name__ == "__main__":
    # Entities linking
    #triple_csvfile = "../data/triples/triples.csv"
    #triple_outfilepath = "../data/triples/triples-elinked.csv"
    #linkents_filepath="../data/linked-ents.json"
    args = getargs()
    triple_csvfile = args['input']
    triple_outfilepath = args['output']
    links_outfilepath = args['save-links']
    df = pd.read_csv(triple_csvfile)
    """
    entslinkd, df = linkents(df)
    with open(linkents_filepath, 'w') as f:
        json.dump(entslinkd, f)
    df.to_csv(triple_outfilepath, index=None)
    """
    linker = EntityLinker(df)
    links = linker.find_links(keep_line=False)
    df = linker.dataframe # necessary ? 
    df.to_csv(triple_outfilepath, index=False)
    #TODO do the linking
    if links_outfilepath is not None:
        with open(links_outfilepath, 'w') as f:
            links_json = {k:v for k, v in links}
            f.write(json.dumps(links_json))
    #print(links)
    print("Number of links {}".format(len(links)))
    
    
    

