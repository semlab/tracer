import pandas as pd


if __name__ == "__main__":
    org_pers = ['ORGANIZATION', 'PERSON']
    triple_df = pd.read_csv("../triplex/output/triples.csv")
    org_pers_subj = triple_df['SUBJ_ENT_TYPE'] in org_pers 
    org_prod_obj = triple_df['OBJ_ENT_TYPE'] in org_pers
    org_pers_df = triple_df[org_pers_subj & org_pers_obj]