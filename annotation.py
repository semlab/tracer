import os
import csv
import xlsxwriter
import numpy as np
import pandas as pd
import random


def random_annotation(inputpath, labelspath, outputpath=None, 
        overwrite=False, labels_col="SUBCATEGORY"):
    if outputpath is None and overwrite is False:
        raise ValueError("Provide an output file path or set overwrite to True.")
    elif not overwrite and outputpath is None:
        # todo replace with inputpath + datetime . extention
        outputpath = inputpath 
    df = pd.read_csv(inputpath)
    labels_df = pd.read_csv(labelspath)
    labels = labels_df[labels_col]
    annotations = [random.choice(labels) for _ in range(df.shape[0])]
    df["RELATION_TYPE"] = annotations
    df.to_csv(outputpath, index=False)


def gen_annotation_files(csvinputpath, labels_filepath, 
        batch_size=1000, sheet_names=['Sheet1', 'Sheet2'], 
        label_col="SUBCATEGORY",
        file_prefix="batch",
        outfolder="../data/annotations/splits"):
    labels_df = pd.read_csv(labels_filepath)
    labels = ['NONE', 'ERRONEOUS']
    trace_labels = labels_df[label_col]
    labels.extend(list(trace_labels))
    df = pd.read_csv(csvinputpath)
    df = df[["SENTENCE", "SUBJECT", "RELATION", "OBJECT"]]
    df["RELATION_TYPE"] = ['NONE'] * df.shape[0]
    df['COMMENT'] = [''] * df.shape[0]
    count = df.shape[0]
    batches = count // batch_size
    if count % batch_size != 0: 
        batches += 1
    df_splits = np.array_split(df, batches)
    for batch, df_split in enumerate(df_splits):
        filename = file_prefix + str(batch) + ".xlsx"
        filepath = os.path.join(outfolder, filename)
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        df_split.to_excel(writer, sheet_name=sheet_names[0])
        workbook = writer.book
        worksheet = writer.sheets[sheet_names[0]]
        label_col_row = 5
        worksheet.data_validation(1, label_col_row, 
            df_split.shape[0], label_col_row, {
                'validate': 'list', 
                'source': labels
            })
        labels_df.to_excel(writer, sheet_name=sheet_names[1])
        writer.save()
        #df_split.to_csv("batch-"+str(batch))

    

if __name__ == "__main__":
    #gen_annotation_files("../data/entslink-triples.csv", 
    #       "../data/labels/trace-labels.csv", batch_size=50)
    random_annotation("../data/triples/triples-elinked.csv", 
            "../data/labels/trace-labels.csv", 
            outputpath="../data/triples/triples-elinked-rand-lbl.csv")
