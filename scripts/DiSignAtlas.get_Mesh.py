"""Disease Mapping
Here we are interested in Mapping the diseases to the corresponding MeSH terms.

Structure:
    1. Imports, Variables and Functions
    2. Load Data
    3. Disease Mapping
"""

# 1. Imports, Variables and Functions
# imports
import pandas as pd, numpy as np, os, sys, re, json, pickle, time, datetime, random
import requests
import xml.etree.ElementTree as ET
import logging
import json
from fuzzywuzzy import fuzz
from tqdm import tqdm
import spacy

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# variables
data_path = os.path.join('..', 'data','DiSignAtlas','dis_info_datasets')
mesh_file_path = "../data/MeSH/desc2023.xml"
output_path = os.path.join("..","results","files", 
                                       "DiSignAtlas",'disease_mapping.nlp.csv'
                                       )
# functions

def build_mesh_term_tree_number_mapping(mesh_xml_file_path: str) -> dict:
    """
    Build a mapping of MeSH terms to their tree numbers from the MeSH XML file.

    Parameters:
    - mesh_xml_file_path (str): The file path to the MeSH XML file.

    Returns:
    - dict: A dictionary where keys are MeSH terms and values are lists of associated tree numbers.
    """
    tree = ET.parse(mesh_xml_file_path)
    root = tree.getroot()

    mesh_term_2_symbol = dict()
    mesh_symbol_2_term = dict()
    for descriptor in root.findall("DescriptorRecord"):
        term = descriptor.find("DescriptorName/String").text
        tree_numbers = [
            tree_number.text
            for tree_number in descriptor.findall("TreeNumberList/TreeNumber")
        ]
        for tree_number in tree_numbers:
            mesh_symbol_2_term[tree_number] = term
        mesh_term_2_symbol[term] = tree_numbers

    return mesh_term_2_symbol, mesh_symbol_2_term

def find_best_fuzzy_match(query, choices):
    """Find Best Fuzzy Match
    Finds the best fuzzy match for a query in a list of choices.
    Arguments:
        query (str): The query string.
        choices (list): A list of strings to search.
    Returns:    
        best_match (str): The best fuzzy match.
        best_score (int): The similarity score of the best match.
    """
    best_match = None
    best_score = 0
    
    for choice in choices:
        similarity_score = fuzz.ratio(query, choice)
        
        if similarity_score > best_score:
            best_score = similarity_score
            best_match = choice
    
    return best_match, best_score

def cosine_similarity(vector1, vector2):
    """Cosine Similarity between two spacy vectors
    Arguments:
        vector1 (spacy.tokens.doc.Doc): The first vector.
        vector2 (spacy.tokens.doc.Doc): The second vector.
    Returns:
        similarity (float): The cosine similarity between the two vectors.
    """
    return vector1.similarity(vector2)

# 2. Load Data
# load disease info
df_disease_info = pd.read_csv(data_path)

diseases = df_disease_info['disease'].unique().tolist()

logging.info(f"Total of {len(diseases)} unique diseases in DiSignAtlas.")

# load disease mapping
mesh_term_2_symbol, mesh_symbol_2_term = build_mesh_term_tree_number_mapping(
    mesh_file_path
)
disease_mesh_terms = list()

for term, symbols in mesh_term_2_symbol.items():
    for symbol in symbols:
        if symbol.startswith("C"):
            disease_mesh_terms.append(term)
            break

logging.info(f"Found {len(disease_mesh_terms)} disease MeSH terms from a total of {len(mesh_term_2_symbol.keys())} terms.")


# 3. Disease Mapping
# map diseases to MeSH terms

# Discarded because it takes too long to run ! ! !
# disease_mapping = list() 

# for disease in tqdm(diseases):
#     best_match, best_score = find_best_fuzzy_match(disease, disease_mesh_terms)
#     disease_mapping.append([disease, best_match, best_score])


# Load the 'en_core_web_md' model
nlp = spacy.load("en_core_web_md")

# Perform disease mapping
disease_mapping = list()

for query_disease in tqdm(diseases):
    query_vector = nlp(query_disease)
    most_similar_disease = None
    highest_similarity = -1  # Initialize with a low value

    for reference_disease in disease_mesh_terms:
        reference_vector = nlp(reference_disease)
        similarity_score = cosine_similarity(query_vector, reference_vector)

        if similarity_score > highest_similarity:
            highest_similarity = similarity_score
            most_similar_disease = reference_disease

    disease_mapping.append([query_disease, most_similar_disease, highest_similarity])


output_path = os.path.join("..", "results", "files", "DiSignAtlas", "disease_mapping.nlp.pkl")

# save disease mapping
df_disease_mapping = pd.DataFrame(disease_mapping, columns=['disease', 'mesh_term', 'score'])
df_disease_mapping.to_csv(output_path, index=False)

logging.info(f"Saved disease mapping to {output_path}.")