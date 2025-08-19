#%%
import json
from rapidfuzz import fuzz, process
#%%
small = "mcu"
big = "marvel"
#%%
mappings_file_small = "./_input/mappings/" + small + ".json"
mappings_file_big = "./_input/mappings/" + big + ".json"

exact_match_file = "./_input/exact_match_all/" + small + "-" + big + ".json"
exact_match_deduplicated_file = "./_input/exact_match_deduplicated/" + small + "-" + big + ".json"
#%%
with open(mappings_file_small) as file:
    mappings_small = {str(v): k for k, v in json.load(file).items()}
    mappings_small_reversed = {v: k for k, v in mappings_small.items()}

with open(mappings_file_big) as file:
    mappings_big = {str(v): k for k, v in json.load(file).items()}
    mappings_big_reversed = {v: k for k, v in mappings_big.items()}

with open(exact_match_file) as emf:
    exact_match = json.load(emf)
#%%
len(exact_match)
#%%
keep_exact_match = list()
#%%
exact_match_rightleft_dict = dict()

for em in exact_match:
    if em[1] in exact_match_rightleft_dict:
        exact_match_rightleft_dict[em[1]].append(em[0])
    else:
        exact_match_rightleft_dict[em[1]] = [em[0]]
#%%
count_rightleft_duplicates = 0

for k, v in exact_match_rightleft_dict.items():
    if len(v) > 1:
        count_rightleft_duplicates += 1
#%%
print("Rightleft Single:", len(exact_match_rightleft_dict) - count_rightleft_duplicates)
print("Rightleft Multiple:",  count_rightleft_duplicates)
#%%
len(exact_match_rightleft_dict)
#%%
for k, v in exact_match_rightleft_dict.items():
    if len(v) > 1:
        type_right = k.split("/")[4]
        keep_left = [item for item in v if item.split("/")[4] == type_right]
        if len(keep_left) > 0:
            best_match, score, _ = process.extractOne(k, keep_left, scorer=fuzz.ratio)
            keep_exact_match.append([best_match, k])
    else:
        keep_exact_match.append([v[0], k])
#%%
len(keep_exact_match)
#%%
exact_match_leftright_dict = dict()

for kem in keep_exact_match:

    if kem[0] in exact_match_leftright_dict:
        exact_match_leftright_dict[kem[0]].append(kem[1])
    else:
        exact_match_leftright_dict[kem[0]] = [kem[1]]
#%%
count_leftright_duplicates = 0

for k, v in exact_match_leftright_dict.items():
    if len(v) > 1:
        count_leftright_duplicates += 1
#%%
print("Leftright Single:", len(exact_match_leftright_dict) - count_leftright_duplicates)
print("Leftright Multiple:",  count_leftright_duplicates)
#%%
len(exact_match_leftright_dict)
#%%
keep_exact_match = list()
#%%
for k, v in exact_match_leftright_dict.items():
    if len(v) > 1:
        type_left = k.split("/")[4]
        keep_right = [item for item in v if item.split("/")[4] == type_left]
        if len(keep_right) > 0:
            best_match, score, _ = process.extractOne(k, keep_right, scorer=fuzz.ratio)
            keep_exact_match.append([k, best_match])
    else:
        keep_exact_match.append([k, v[0]])
#%%
len(keep_exact_match)
#%%
exact_match_leftright_dict = dict()
exact_match_rightleft_dict = dict()

for em in keep_exact_match:

    if em[0] in exact_match_leftright_dict:
        exact_match_leftright_dict[em[0]].append(em[1])
    else:
        exact_match_leftright_dict[em[0]] = [em[1]]

    if em[1] in exact_match_rightleft_dict:
        exact_match_rightleft_dict[em[1]].append(em[0])
    else:
        exact_match_rightleft_dict[em[1]] = [em[0]]
#%%
count_leftright_duplicates = 0
count_rightleft_duplicates = 0

for k, v in exact_match_leftright_dict.items():
    if len(v) > 1:
        count_leftright_duplicates += 1

for k, v in exact_match_rightleft_dict.items():
    if len(v) > 1:
        count_rightleft_duplicates += 1
#%%
len(keep_exact_match)
#%%
print("Leftright Single:", len(keep_exact_match) - count_leftright_duplicates)
print("Leftright Multiple:",  count_leftright_duplicates)
print()
print("Rightleft Single:", len(keep_exact_match) - count_rightleft_duplicates)
print("Rightleft Multiple:",  count_rightleft_duplicates)
#%%
with open(exact_match_deduplicated_file, "w") as f:
    json.dump(keep_exact_match, f, indent=4)
#%%
