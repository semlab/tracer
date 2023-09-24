import argparse
import pandas as pd
import numpy as np 
from sklearn.cluster import KMeans
from gensim.models import Word2Vec

def wv_key(word):
    return word.lower().replace(' ', '_')


def assign_relation_types(dataframe, subj_ent_types, obj_ent_types, n_types=2, labels_offset=0):
    entity_types_df = dataframe[
        dataframe['SUBJ_ENT_TYPE'].isin(subj_ent_types) & 
        dataframe['OBJ_ENT_TYPE'].isin(obj_ent_types)
    ]
    data = [embeddings.wv[wv_key(subj)] - embeddings.wv[wv_key(obj)] 
        for subj, obj in zip(entity_types_df['SUBJ_ENT'], entity_types_df['OBJ_ENT'])
    ]
    kmeans = KMeans(n_clusters=n_types)
    kmeans.fit(data)
    entity_types_df['REL_TYPE'] = [label + labels_offset for label in kmeans.labels_]
    #assignments = assign_cluster(data)
    #entity_types_df['REL_TYPE'] = assignments
    return entity_types_df



def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, 
            help="input triples file (prepared by the triplex command)")
    parser.add_argument('-o', '--output', required=False, 
            help="file path to save the new df")
    parser.add_argument('--embeddings', required=False, 
            help="path to load the embeddings")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['embeddings'] = args.embeddings
    return args_dict


if __name__ == "__main__":
    args = getargs()
    triples_path = args['input']
    outfilepath = 'triple-categorized.csv' if args['output'] is None else args['output']
    embeddings_path = args['embeddings']
    embeddings = Word2Vec.load(embeddings_path)
    vocab = embeddings.wv.index_to_key
    triple_df = pd.read_csv(triples_path)
    triple_df['REL_TYPE'] = 'N/A'
    triple_df['SUBJ_KEY'] = [wv_key(ent) for ent in triple_df['SUBJ_ENT']]
    triple_df['OBJ_KEY'] = [wv_key(ent) for ent in triple_df['OBJ_ENT']]
    triple_df = triple_df[triple_df['SUBJ_KEY'].isin(vocab) & triple_df['OBJ_KEY'].isin(vocab)]
    triple_df = triple_df[triple_df['SUBJ_KEY'] != 'he']
    triple_df = triple_df[triple_df['OBJ_KEY'] != 'he']
    org_pers_df = assign_relation_types(triple_df, ['ORGANIZATION', 'PERSON'], ['ORGANIZATION', 'PERSON'], n_types=2)
    org_prod_df = assign_relation_types(triple_df, ['ORGANIZATION'], ['COMMODITY'], n_types=2, labels_offset=2)
    org_place_df = assign_relation_types(triple_df, ['ORGANIZATION'], ['LOCATION'], n_types=1, labels_offset=4)
    triple_categ_df = pd.concat([org_pers_df, org_prod_df, org_place_df], axis=0)
    triple_categ_df = triple_categ_df.sort_values(by='Id', ascending=True)
    triple_categ_df[['Id', 'SENTENCE', 'SUBJ_ENT', 'OBJ_ENT','SUBJ_ENT_TYPE', 'OBJ_ENT_TYPE', 'REL_TYPE']].to_csv(outfilepath)


