"""
iLINCS freeze script

This script is used to freeze the iLINCS database. 

Structure:
    1. Imports, Variables, Functions
    2. Retrieve Data
    3. Parse & Store Data

"""

# 1. Imports, Variables, Functions
# imports
import requests, os
import pandas as pd
import logging, time

# Reconfigure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("iLINCS Freeze: CSV")

# variabels
OUTPUT_PATH = "../data/iLINCS"


# functions
def get_signatures():
    """
    get_signatures
    Retrieves a list of signatures from the iLINCS API.

    Parameters:
    - None

    Returns:
    - List[Dict]:
        A list of dictionaries, each representing a signature. Returns None in case of failure.
    """
    url = "http://www.ilincs.org/api/SignatureMeta?"
    url = "http://www.ilincs.org/api/SignatureMeta?"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve data")
        return None


def get_datasets():
    """
    get_datasets
    Retrieves a list of datasets from the iLINCS API.

    Parameters:
    - None

    Returns:
    - List[Dict]:
        A list of dictionaries, each representing a dataset. Returns None in case of failure.
    """
    # url = 'http://www.ilincs.org/api/PublicDatasets?filter={"limit":1000}'
    url = "http://www.ilincs.org/api/PublicDatasets?"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve datasets")
        return None


def get_genes():
    """
    get_genes
    Retrieves gene information from the iLINCS API.

    Parameters:
    - None

    Returns:
    - List[Dict]:
        A list of dictionaries, each representing a gene. Returns None in case of failure.
    """
    url = "http://www.ilincs.org/api/GeneInfos?"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve genes")
        return None


def get_compounds():
    """
    get_compounds
    Retrieves a list of compounds from the iLINCS API.

    Parameters:
    - None

    Returns:
    - List[Dict]: A list of dictionaries, each representing a compound. Returns None in case of failure.
    """
    url = "http://www.ilincs.org/api/Compounds?"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve compounds")
        return None


def save_to_csv(data, filename):
    """
    save_to_csv
    Saves given data to a CSV file.

    Parameters:
    - data: List[Dict]
        The data to be saved into a CSV file.
    - filename: str
        The name of the file to save the data into.

    Returns:
    - df
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

    return df

def download_batch_signature_data(
    signature_ids, no_of_top_genes, display, batch_size=10
):
    """
    Download iLINCS Signature Data - optimized for Batch downloads

    Arguments:
    - signature_ids: list of str
        List of signature IDs
    - no_of_top_genes: int
        Number of top differentially expressed genes
    - display: bool
        Whether to display the data
    - batch_size: int
        Number of signatures to download in each batch

    Returns:
    - processed_data: dict
        Dictionary with SignatureID -> [{}]
    """
    endpoint = "http://www.ilincs.org/api/ilincsR/downloadSignature"
    processed_data = {}

    for i in range(0, len(signature_ids), batch_size):
        print(f"Batch {i}", end="\r")

        batch_ids = signature_ids[i : i + batch_size]
        data = {
            "sigID": ",".join(batch_ids),
            "noOfTopGenes": no_of_top_genes,
            "display": display,
        }
        response = requests.post(endpoint, data=data)
        if response.status_code == 200:
            raw_data = response.json()
            for item in raw_data["data"]["signature"]:
                signatureID = item["signatureID"]
                if signatureID not in processed_data:
                    processed_data[signatureID] = []
                processed_data[signatureID].append(item)

        else:
            print(
                f"Error in batch {i // batch_size + 1}: {response.status_code}, {response.text}"
            )

    print()
    return processed_data
def download_signature_data(signature_ids, no_of_top_genes, display):
    """
    Download iLINCS Signature Data

    Arguments:
    - signature_ids: list()
        List of signature IDs
    - no_of_top_genes: int()
        Nº of top DE genes
    - display: bool()

    Returns:
    - respose.json()
        Response obtained
    """
    endpoint = "http://www.ilincs.org/api/ilincsR/downloadSignature"
    data = {
        "sigID": ",".join(signature_ids),
        "noOfTopGenes": no_of_top_genes,
        "display": display,
    }
    response = requests.post(endpoint, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

def download_batch_signature_data(
    signature_ids, no_of_top_genes, display, batch_size=10, retries=10, timeout=300
):
    """
    Download iLINCS Signature Data - optimized for Batch downloads

    Arguments:
    - signature_ids: list of str
        List of signature IDs
    - no_of_top_genes: int
        Number of top differentially expressed genes
    - display: bool
        Whether to display the data
    - batch_size: int
        Number of signatures to download in each batch

    Returns:
    - processed_data: dict
        Dictionary with SignatureID -> [{}]
    """
    endpoint = "http://www.ilincs.org/api/ilincsR/downloadSignature"
    processed_data = {}

    for i in range(0, len(signature_ids), batch_size):
        logging.info(f"Batch {i}")

        batch_ids = signature_ids[i : i + batch_size]
        data = {
            "sigID": ",".join(batch_ids),
            "noOfTopGenes": no_of_top_genes,
            "display": display,
        }

        for attempt in range(retries):
            try:
                response = requests.post(endpoint, data=data, timeout=timeout)
                if response.status_code == 200:
                    raw_data = response.json()
                    for item in raw_data["data"]["signature"]:
                        signatureID = item["signatureID"]
                        if signatureID not in processed_data:
                            processed_data[signatureID] = []
                        processed_data[signatureID].append(item)
                    break
                else:
                    logging.error(f"Error in batch {i // batch_size + 1}: {response.status_code}, {response.text}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.Timeout:
                logging.error(f"Timeout occurred in batch {i // batch_size + 1}, attempt {attempt + 1}")
                time.sleep(2 ** attempt)  # Exponential backoff

    return processed_data


# 2. Retrieve Data
# get signatures
signatures = get_signatures()
logging.info(f"Nº Retrieved Signatures {len(signatures)}")

# get datasets
datasets = get_datasets()
logging.info(f"Nº Retrieved Datasets {len(datasets)}")

# get genes
genes = get_genes()
logging.info(f"Nº Retrieved Genes {len(genes)}")

# get compounds
compounds = get_compounds()
logging.info(f"Nº Retrieved Compounds {len(compounds)}")

# get signature vectors for diseases
# get signature ids
df_signatures = pd.DataFrame(signatures)
disease_signatureIDs = df_signatures[df_signatures["libraryid"] == "LIB_1"][
    "signatureid"
].unique()
logging.info(f"Nº Disease Signatures {len(disease_signatureIDs)}")

# download signature data
signature_vectors = download_batch_signature_data(signature_ids=disease_signatureIDs, 
                                                  no_of_top_genes=100000,
                                                  display=True, 
                                                  batch_size=10)

# 3. Parse & Store Data
# parse & store signatures
df_signatures = save_to_csv(signatures, os.path.join(OUTPUT_PATH, "signatures.csv"))

# parse & store datasets
df_datasets = save_to_csv(datasets, os.path.join(OUTPUT_PATH, "datasets.csv"))

# parse & store genes
df_genes = save_to_csv(genes, os.path.join(OUTPUT_PATH, "genes.csv"))

# parse & store compounds
df_compounds = save_to_csv(compounds, os.path.join(OUTPUT_PATH, "compounds.csv"))

# parse & store signature vectors
for signature_id, data in signature_vectors.items():
    df_signature = save_to_csv(
        data=data, 
        filename=os.path.join(OUTPUT_PATH, "signature_vectors" ,f"{signature_id}.csv")
    )
