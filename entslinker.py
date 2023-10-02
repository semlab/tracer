#!/usr/bin/python3

import argparse
import os
import json
import pandas as pd

        


class EntityLinker:

    def __init__(self, dataframe):
        """ dataframe from triplex"""
        self.pronouns = ["he", "she", "it", "they"]
        self.dataframe = dataframe
        self.links_df = None
        self.cleaned_df = None
        self.links = set() 
        self.lookup = dict()
        pass


    def filter_out_pronouns(self, row):
        subj_not_pronouns = row['SUBJ_ENT'] not in self.pronouns
        obj_not_pronouns = row['OBJ_ENT'] not in self.pronouns
        return subj_not_pronouns and obj_not_pronouns


    def is_link(self, row):
        subj_ent = row['SUBJ_ENT']
        obj_ent = row['OBJ_ENT']
        not_pronouns = subj_ent not in self.pronouns and obj_ent not in self.pronouns
        same_entity_type = (row['SUBJ_ENT_TYPE'] == row['OBJ_ENT_TYPE']) 
        be_relation = row['RELATION'] == 'be'
        has_acronym = subj_ent.isupper() or obj_ent.isupper()
        return not_pronouns and same_entity_type and be_relation and has_acronym # TODO make has_acronym optional


    def is_not_link(self, row):
        return not self.is_link(row)


    def filter_links(self):
        df = self.dataframe[self.dataframe.apply(self.filter_out_pronouns, axis=1)]
        self.links_df = df[df.apply(self.is_link, axis=1)]
        self.cleaned_df = df[df.apply(self.is_not_link, axis=1)]


    def run(self):
        self.filter_links()


    def find_links(self, keep_line=True):
        """list entities links from a dataframe from triplex
           keep_line: whether to remove the line representing a link
        """
        links = set()
        for idx, row in df.iterrows():
            subj = row['SUBJECT']
            obj = row['OBJECT']
            rel = row['RELATION']
            not_pronouns = subj not in self.pronouns and obj not in self.pronouns
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
            help="output with entity links filtered out csv")
    parser.add_argument('--save-links', required=False,
            help="save the identified links")
    parser.add_argument('--save-lookup', required=False,
            help="save the lookup table for links")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['save-links'] = args.save_links
    args_dict['save-lookup'] = args.save_links
    return args_dict



if __name__ == "__main__":
    # Entities linking
    #triple_csvfile = "../data/triples/triples.csv"
    #triple_outfilepath = "../data/triples/triples-elinked.csv"
    #linkents_filepath="../data/linked-ents.json"
    """
    entslinkd, df = linkents(df)
    with open(linkents_filepath, 'w') as f:
        json.dump(entslinkd, f)
    df.to_csv(triple_outfilepath, index=None)
    """
    """
    args = getargs()
    triple_csvfile = args['input']
    triple_outfilepath = args['output']
    links_outfilepath = args['save-links']
    df = pd.read_csv(triple_csvfile)
    """
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
    """

    args = getargs()
    inputpath = args['input']
    outputpath = args['output']
    linkspath = args['save-links']
    lookuppath = args['save-lookup']
    df = pd.read_csv(inputpath)

    linker = EntityLinker(df)
    linker.run()
    linker.cleaned_df.to_csv(outputpath)
    if linkspath is not None: # Save links df
        linker.links_df.to_csv(linkspath)
    if lookuppath:
        pass # create lookup and save
    
    print(len(df))
    print(len(linker.links_df))
    print(len(linker.cleaned_df))

    
    
    

