import os
import argparse
import csv
import xlsxwriter
import numpy as np
import pandas as pd
import random


def random_annotation(inputpath, labelspath, outputpath=None, 
        overwrite=False, labels_col="SUBCATEGORY"):
    """
    Generate annotation files from extracted triples.
    :param inputpath: (csv) triples file path
    :param labelspath: (csv) file path of the possible labels
    :param outputpath: (csv) file path of the randomly labelled triples
    """
    # TODO is the overwrite thing necessary ?
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
        outfolder="."):
        #outfolder="../data/annotations/splits"):
    """
    Generate annotation files from extracted triples.
    :param csvinputpath: (csv) triples file path
    :param labels_filepath: (csv) file path of the possible labels
    """
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




def merge_annotations(inputpath, outputpath):
    """
    To merge annotated triple relationships from differents 
    human annotated (excel) files.
    :param inputpath: Path to the folder of different annotation files
    :param outpupath: Output file of the merged annotations
    """
    filenames = [filename for filename in  sorted(os.listdir(inputpath))
        if filename.endswith(".xlsx")]
    frames = []
    for filename in filenames:
        annotationed_df = pd.read_excel(os.path.join(inputpath,filename))
        filtered_df = annotationed_df[annotationed_df["RELATION_TYPE"] != "NONE"]
        filtered_df = filtered_df[filtered_df["RELATION_TYPE"] != ""]
        frames.append(filtered_df)
    merged_df = pd.concat(frames)
    merged_df.to_csv(outputpath, index=False)



def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to run on the annotations')
    parser.add_argument('-i', '--input', required=True, 
            help="input tokens file (prepared by the triplex command)")
    parser.add_argument('-o', '--output', required=True, 
            help="file path to save the vectors")
    parser.add_argument('-l', '--labels', required=False, 
            help="labels used to generate annotation files")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['action'] = args.action
    args_dict['labels'] = args.labels
    return args_dict
    

if __name__ == "__main__":
    args = getargs()
    action = args['action']
    labelspath = args['labels']
    inputpath = args['input']
    outputpath = args['output']
    if action == 'generate':
        gen_annotation_files(inputpath, labelspath, outfolder=outputpath, 
                batch_size=50)
    elif action == 'random':
        random_annotation(inputpath, labelspath, outputpath=outpupath)
    elif action == 'merge':
        merge_annotations(inputpath, outputpath)
    else:
        raise ValueError('sub command shoud be generate, random of merge')

