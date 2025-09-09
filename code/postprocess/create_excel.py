import os
import json
import pandas as pd
import openpyxl


files4 = {
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_long_top1/stats.json": "union_dogtag_long_top1",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_long_reranked100_deduplicated/stats.json": "union_dogtag_long_reranked100_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_long_top10pairs_llm_notstrict_deduplicated/stats.json": "union_dogtag_long_top10pairs_llm_notstrict_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_long_top10pairs_llm_strict_deduplicated/stats.json": "union_dogtag_long_top10pairs_llm_strict_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_2sentences_top1/stats.json": "union_dogtag_short_2sentences_top1",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_2sentences_reranked100_deduplicated/stats.json": "union_dogtag_short_2sentences_reranked100_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_2sentences_top10pairs_llm_notstrict_deduplicated/stats.json": "union_dogtag_short_2sentences_top10pairs_llm_notstrict_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_2sentences_top10pairs_llm_strict_deduplicated/stats.json": "union_dogtag_short_2sentences_top10pairs_llm_strict_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_top1/stats.json": "union_dogtag_short_top1/stats.json",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_reranked100_deduplicated/stats.json": "union_dogtag_short_reranked100_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_top10pairs_llm_notstrict_deduplicated/stats.json": "union_dogtag_short_top10pairs_llm_notstrict_deduplicated",
    "/Users/matevass/Documents/Projects/KGEntityMatching-Public/results_union/union_dogtag_short_top10pairs_llm_strict_deduplicated/stats.json": "union_dogtag_short_top10pairs_llm_strict_deduplicated",
}

container = dict()

files_dict = files4

for path, val in files_dict.items():
    with open(path, "r") as f:
        data = json.load(f)
        last_folder = os.path.basename(os.path.dirname(os.path.normpath(path)))
        container[val] = data

metrics = ["Precision", "Recall", "F1"]
datasets = ["mcu-marvel", "memoryalpha-memorybeta", "stexpanded-memoryalpha", "swg-starwars", "swtor-starwars"]


def get_columns():
    cols = list()
    for ds in datasets:
        for m in metrics:
            cols.append(tuple([ds, m]))

    return cols


columns = pd.MultiIndex.from_tuples(get_columns())
data = list()

for algoname, row in container.items():
    record = list()
    for ds in datasets:
        if ds in row:
            record.extend(row[ds])
        else:
            record.extend([0,0,0])
    data.append(record)

df = pd.DataFrame(data,
                  columns=columns,
                  index=list(container.keys())
                  )

df.to_excel("/Users/matevass/Documents/Projects/KGEntityMatching-Public/test.xlsx")
