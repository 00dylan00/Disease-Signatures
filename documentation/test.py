""" Perform MSA ClustalW

Structure:  
    1. Imports, Variables, Functions
    2. Load Data
    3. Perform MSA
    4. Save Results
"""

# 1. Imports, Variables, Functions
# imports
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, statistics, sys, os
from Bio import SeqIO, AlignIO
from Bio.Align.Applications import ClustalwCommandline
from Bio.Align import AlignInfo
from collections import Counter

# variables
path_refseq_blastp = "pblb_refseq_prot_1000_pblb.fas"
path_refseq_output = "./"


# functions
# functions
def get_consensus_identity_list(msa, consensus_seq, msa_count, start=None, end=None):
    """Get consensus identity list for a specified range of positions in an MSA.

    Parameters
    ----------
    msa : list[str]
        List of sequences in the MSA.
    consensus_seq : str
        Consensus sequence.
    msa_count : int
        Number of sequences in the MSA.
    start : int, optional
        Start position. If None, `0` is set.
    end : int, optional
        End position. If None, `alignment_length` is set.

    Returns
    -------
    consensus_identity_list : list[float]
        Consensus identity list (0 - 100 [%])
    """
    start = 0 if start is None else start
    end = len(consensus_seq) if end is None else end
    consensus_identity_list = []

    for idx in range(start, end):
        column_chars = "".join(seq[idx] for seq in msa)
        counter = Counter(filter(lambda c: c not in ("-", "*"), column_chars))
        count = counter.most_common()[0][1] if len(counter) != 0 else 0
        consensus_identity = (count / msa_count) * 100
        consensus_identity_list.append(consensus_identity)

    return consensus_identity_list
# 2. Load Data
in_file = os.path.join(path_refseq_blastp)

if os.path.exists(os.path.join("aligned_sequences.refseq.clustal")):
    alignment_refseq = AlignIO.read(
        os.path.join("aligned_sequences.refseq.clustal"))
else:
    # 3. Perform MSA
    clustalw_cline = ClustalwCommandline(
        "clustalw",
        infile=in_file,
        outfile=os.path.join(path_refseq_output, "aligned_sequences.clustal"),
    )
    stdout, stderr = clustalw_cline()

    print("STDERR:", stderr)

    # 4. Save Results
    alignment_refseq = AlignIO.read(
        os.path.join(path_refseq_output, "aligned_sequences.clustal"),
        "clustal",
    )

    AlignIO.write(
        alignment_refseq,
        os.path.join(path_refseq_output, "aligned_sequences.fasta"),
        "fasta",
    )
# get consensus sequence
# Create a summary info object
summary_refseq_info = AlignInfo.SummaryInfo(alignment_refseq)

# Calculate the consensus sequence
consensus_refseq = summary_refseq_info.dumb_consensus()

# get consensus percentage identity
values = get_consensus_identity_list(
    msa=alignment_refseq,
    consensus_seq=consensus_refseq,
    msa_count=len(alignment_refseq),
)
# imports
import matplotlib.pyplot as plt
import numpy as np
from Bio import AlignIO

# variables
# Define colors for residues (you can customize these)
# RasMol Color scheme:
# * http://acces.ens-lyon.fr/biotic/rastop/help/colour.htm
colors = {
    "A": (0.7843, 0.7843, 0.7843),  # Dark Grey
    "C": (1.0, 1.0, 0.0),  # Yellow
    "D": (0.9216, 0.2941, 0.2157),  # Bright Red
    "E": (0.9216, 0.2941, 0.2157),  # Bright Red
    "F": (0.1961, 0.1961, 0.6667),  # Mid Blue
    "G": (0.9216, 0.9216, 0.9216),  # Light Grey
    "H": (0.5098, 0.5098, 0.8235),  # Pale Blue
    "I": (0.0588, 0.5098, 0.0588),  # Green
    "K": (0.0784, 0.3529, 1.0),  # Blue
    "L": (0.0588, 0.5098, 0.0588),  # Green
    "M": (1.0, 1.0, 0.0),  # Yellow
    "N": (0.0, 0.8627, 0.8627),  # Cyan
    "P": (0.8627, 0.5882, 0.5098),  # Flesh
    "Q": (0.0, 0.8627, 0.8627),  # Cyan
    "R": (0.0784, 0.3529, 1.0),  # Blue
    "S": (1.0, 0.5882, 0.0),  # Orange
    "T": (1.0, 0.5882, 0.0),  # Orange
    "V": (0.0588, 0.5098, 0.0588),  # Green
    "W": (0.7059, 0.3529, 0.7059),  # Pink
    "Y": (0.1961, 0.1961, 0.6667),  # Mid Blue
    "-": "white",  # white
}

# functions

# Dynamically adjust the figure height based on the number of sequences
alignment_height = len(alignment_refseq)
fig_height = max(8, 8)  # Adjust the divisor as needed to scale the plot appropriately

fig, (ax1, ax2) = plt.subplots(
    2,
    1,
    figsize=(8, fig_height),
    sharex=True,
    gridspec_kw={"hspace": 0.05, "height_ratios": [8, 1]},
)


# Plot the MSA as boxes
alignment_width = len(alignment_refseq[0].seq)
residue_height = 1

for i, record in enumerate(alignment_refseq):
    seq = str(record.seq)
    for j, residue in enumerate(seq):
        color = colors.get(residue, "white")
        ax1.add_patch(
            plt.Rectangle(
                (j, i - 0.5), 1, residue_height, color=color, edgecolor="black"
            )
        )

# Customize the plot (ax1)
ax1.set_xlim(-0.5, alignment_width - 0.5)
ax1.set_ylim(-0.5, alignment_height - 0.5)  # Adjusted to remove unnecessary height
ax1.set_yticks(np.arange(alignment_height))
# ax1.set_yticklabels([record.id for record in alignment_refseq], fontsize=6)
ax1.set_yticklabels([])
ax1.tick_params(axis="y", length=0)  # This removes the y-tick lines
ax1.set_title("Multiple Sequence Alignment with RefSeq Sequences")

# Assuming 'values' for the consensus identity plot are defined
# Plot 2 (Bar plot)
ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax2.bar(range(len(values)), values)
ax2.set_xlabel("Position")
ax2.set_ylabel("Consensus %", rotation=90, fontsize=8)

# Customize the appearance of the second plot
ax2.set_xlim(-0.5, alignment_width - 0.5)

# Adjust the space between the two plots and show/save the merged plot
plt.tight_layout()

# Show the merged plot
plt.savefig(
    os.path.join("msa.refseq.png"),
    dpi=300,
    bbox_inches="tight",
)