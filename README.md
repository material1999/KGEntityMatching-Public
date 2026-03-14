# KG Entity Matching

**Large Language Models for Sparse Entity Alignment over Knowledge Graphs**

This repository contains the implementation of DogMa, a system for entity alignment across knowledge graphs using Large Language Models (LLMs). The system won **first place** in the OAEI Knowledge Graph Track 2025 competition.

## Overview

Entity Alignment (EA) identifies nodes across different knowledge graphs that refer to the same real-world entity. This repository implements a Retrieval-Augmented Generation (RAG) approach for **sparse entity alignment**, where only a small fraction (<10%) of entities have matching pairs across KGs.

### Key Features

- **Textual Entity Representations ("Dogtags")**: Four strategies to combine node descriptions with graph neighborhood information
- **Embedding-based Retrieval**: Efficient candidate retrieval using dense vector embeddings
- **LLM-based Selection**: Multiple selection strategies including exact matching, reranking, and LLM prompting
- **Sparse Alignment Focus**: Designed for real-world scenarios with limited entity overlap

### Approach

1. **Retrieval Phase**: Embed entity representations (dogtags) and retrieve top-K candidates from target KG using cosine similarity
2. **Selection Phase**: Apply selection strategy:
   - Exact string matching (baseline)
   - Embedding-based reranking
   - LLM prompting with candidate entities

## Repository Structure

```
KGEntityMatching-Public/
├── code/                           # Source code
│   ├── preprocess/                 # Data preprocessing scripts
│   │   ├── graph_downloader.py     # Download KG datasets from OAEI
│   │   ├── rdf2triples.py          # Convert RDF to triple format
│   │   └── gold_pair_downloader.py # Download gold standard alignments
│   ├── features/                   # Entity representation (dogtag) generation
│   │   ├── dogtag_short.py         # Short dogtag: label + type + abstract
│   │   ├── dogtag_long.py          # Long dogtag: all node properties
│   │   ├── node_neighbourhood_gather.py  # Extract graph neighborhoods
│   │   └── node_nb_promptgen.py    # Generate prompts for LLM summarization
│   ├── algos/                      # Main algorithms
│   │   ├── exactmatch.py           # Exact string matching baseline
│   │   ├── TopX_pairs.py           # Find top-K candidates via embedding similarity
│   │   ├── Top1_pairs.py           # Select top-1 match from candidates
│   │   ├── Reranked_TopX.py        # Rerank candidates using cross-encoder
│   │   ├── GenAI_input_generator.py           # Generate LLM prompts for selection
│   │   ├── GenAI_input_generator_retrieval.py # Generate prompts with retrieval
│   │   └── utils/                  # Utility functions
│   ├── scripts/                    # Utility scripts
│   │   ├── embedder.py             # Generate embeddings from dogtags
│   │   ├── runprompts.py           # Run LLM inference on prompts
│   │   ├── runprompts_accelerate.py # Accelerated LLM inference
│   │   ├── extract_top10_response.py # Parse LLM responses
│   │   ├── extract_nb_response.py  # Parse neighborhood summaries
│   │   ├── eval_folder.py          # Evaluate alignment results
│   │   └── shuffle_topx.py         # Shuffle candidate order (for analysis)
│   ├── postprocess/                # Post-processing utilities
│   │   ├── exact_match_deduplicate.py  # Remove duplicate exact matches
│   │   ├── score_deduplicate.py    # Remove duplicates by score
│   │   ├── threshold_pairs.py      # Apply confidence threshold
│   │   ├── union_pairs.py          # Combine multiple alignment results
│   │   └── create_excel.py         # Generate result Excel files
│   ├── playground/                 # Experimental notebooks
│   └── commands.txt                # Complete pipeline command sequence
├── data/                           # Downloaded datasets
│   └── links.txt                   # OAEI dataset URL
├── results/                        # Alignment results
├── results_discussion/             # Analysis experiments (shuffle, etc.)
├── results_threshold/              # Threshold-based filtering results
├── results_union/                  # Combined alignment results
└── excel/                          # Result summaries and best configurations
    ├── best_f1/                    # Best F1 configurations per method
    ├── best_f1_union/              # Best F1 with union strategies
    └── best_pairs/                 # Best alignment pairs by dataset
```

## Installation

### Requirements

- Python 3.8+
- PyTorch
- Transformers
- Sentence-Transformers
- NetworkX
- NLTK
- Other dependencies in typical scientific Python stack (numpy, pandas, scikit-learn)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd KGEntityMatching-Public

# Install dependencies
pip install torch transformers sentence-transformers networkx nltk pandas numpy scikit-learn tqdm requests

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

## Usage

The complete pipeline is documented in `code/commands.txt`. Below is a step-by-step guide:

### 1. Preprocessing

Download and prepare the OAEI Knowledge Graph datasets:

```bash
cd code/preprocess

# Download knowledge graph RDF files
python graph_downloader.py

# Convert RDF to triple format
python rdf2triples.py

# Download gold standard alignments
python gold_pair_downloader.py
```

### 2. Generate Entity Representations (Dogtags)

Create textual representations of entities:

```bash
cd code/features

# Short dogtag (all sentences from abstract)
python dogtag_short.py -o <output_path> -s -1

# Short dogtag (first 2 sentences from abstract)
python dogtag_short.py -o <output_path> -s 2

# Long dogtag (all node properties)
python dogtag_long.py -o <output_path>
```

**Dogtag variants:**
- `dogtag_short`: Label + Type + Abstract (configurable sentence count)
- `dogtag_long`: All node properties including relationships
- `dogtag_nb_summaries`: LLM-generated summaries of node neighborhoods

### 3. Generate Embeddings

Create dense vector embeddings of dogtags:

```bash
cd code/scripts

python embedder.py \
  -f <dogtag_folder>/str \
  -o <output_embeddings_folder>
```

### 4. Retrieve Candidate Matches

Find top-K candidate entities from target KG:

```bash
cd code/algos

# Get top-K candidates (e.g., K=10)
python TopX_pairs.py \
  -f <embeddings_folder> \
  -o <output_pairs_folder> \
  -k 10
```

### 5. Selection Strategy

Choose one of three selection strategies:

#### A. Top-1 Selection (embedding-based)

```bash
python Top1_pairs.py \
  -f <topX_pairs_folder> \
  -o <output_folder>
```

#### B. Reranking (cross-encoder)

```bash
python Reranked_TopX.py \
  -d <dogtag_str_folder> \
  -e <embeddings_folder> \
  -o <output_folder> \
  -k 100 \
  --gpu
```

#### C. LLM-based Selection

```bash
# Generate LLM prompts
python GenAI_input_generator.py \
  -p <topX_pairs_folder> \
  -d <dogtag_raw_folder> \
  -o <prompts_output_folder> \
  --method 1  # 1=relaxed, 2=strict

# Run LLM inference (requires GPU cluster or API)
python runprompts.py \
  -f <prompts_folder> \
  -o <llm_responses_folder> \
  -m <model_name>

# Parse LLM responses
python extract_top10_response.py \
  -t <topX_pairs_folder> \
  -r <llm_responses_folder> \
  -o <output_pairs_folder>
```

### 6. Post-processing

#### Deduplication

Remove duplicate alignments:

```bash
cd code/postprocess

# For exact match results
python exact_match_deduplicate.py \
  -i <input_pairs_folder> \
  -o <output_deduplicated_folder>

# For scored results (reranking/LLM)
python score_deduplicate.py \
  -i <input_pairs_folder> \
  -o <output_deduplicated_folder>
```

#### Union of Results

Combine multiple alignment methods:

```bash
python union_pairs.py \
  -em <exact_match_folder> \
  -fp <first_pairs_folder> \
  -o <output_union_folder> \
  -m median  # or 'mean'
```

### 7. Evaluation

Evaluate alignment quality against gold standard:

```bash
cd code/scripts

python eval_folder.py -p <pairs_folder>
```

Outputs precision, recall, F1-score for each dataset pair.

## Advanced Features

### LLM Neighborhood Summaries

Generate LLM summaries of entity neighborhoods for improved representations:

```bash
# 1. Extract neighborhoods
python node_neighbourhood_gather.py \
  -d <dogtag_long_raw_folder> \
  -o <neighborhoods_output>

# 2. Generate prompts for summarization
python node_nb_promptgen.py \
  -d <neighborhoods_str_folder> \
  -o <prompts_output>

# 3. Run LLM to generate summaries
python runprompts.py -f <prompts_folder> -o <summaries_output>

# 4. Parse responses
python extract_nb_response.py \
  -r <llm_summaries_folder> \
  -p <neighborhoods_str_folder> \
  -o <parsed_summaries>

# 5. Embed summaries and continue pipeline
python embedder.py -f <parsed_summaries> -o <embeddings_output>
```

### Shuffle Analysis

Test LLM sensitivity to candidate ordering:

```bash
python shuffle_topx.py \
  -t <topX_pairs_folder> \
  -o <shuffled_output> \
  -r  # random seed
```

## Dataset

This implementation uses the **OAEI Knowledge Graph Track** dataset:
- **Source**: https://oaei.ontologymatching.org/2025/knowledgegraph/index.html
- **Domains**: Star Wars, Marvel, Star Trek fandom wikis
- **Characteristics**: Sparse alignment (<10% overlap), same language, heterogeneous structures

## Results

The `excel/` folder contains:
- **best_f1/**: Best F1 score configurations per method
- **best_f1_union/**: Best F1 scores using union strategies
- **best_pairs/**: Final alignment outputs for submission

Result folders contain JSON files with entity pair alignments and confidence scores.

## Citation

If you use this code, please cite our paper:

```bibtex
TODO
```


## Contact

For questions or issues, please open a GitHub issue or contact the authors.