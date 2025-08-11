#%%
from rdflib import Graph
import os
from urllib.parse import urlparse
import re
from tqdm import tqdm
import json
#%%
graph = "marvel"
output = "./_input/dogtags/" + graph + ".json"
#%%
g = Graph()
g.parse("./_input/rdfxml/" + graph + ".xml", format="xml")
#%%
property_str = None

for prefix, namespace in g.namespaces():
    if str(prefix) == "ns1":
        property_str = str(namespace)

resource_str = property_str.replace("property", "resource")
class_str = property_str.replace("property", "class")
#%%
namespace_list = [
    str(namespace)
    for prefix, namespace in g.namespaces()
    if str(namespace) == property_str or not str(namespace).startswith(property_str)
]
#%%
def clean_value(value):
    s = str(value)
    s = s.replace(resource_str, "")
    s = s.replace(class_str, "")
    s = re.sub(r'\n+', '', s)
    for sub in namespace_list:
        s = s.replace(sub, " ")
    return s.strip()

def is_image_url(url):
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"}
    path = urlparse(url).path
    ext = os.path.splitext(path.lower())[1]
    return ext in image_extensions

def is_wikiPageWikiLink(value):
    return "wikiPageWikiLink" in str(value)

def is_wikiPageExternalLink(value):
    return "wikiPageExternalLink" in str(value)
#%%
# test_entity = "http://dbkwik.webdatacommons.org/stexpanded.wikia.com/resource/Magna_Roma"
# test_entity = "http://dbkwik.webdatacommons.org/stexpanded.wikia.com/resource/William_T._Riker"
# test_entity = "http://dbkwik.webdatacommons.org/stexpanded.wikia.com/resource/James_T._Kirk_(Phase_II)"
# test_entity = "http://dbkwik.webdatacommons.org/memory-alpha.wikia.com/resource/Roman_Empire_(892-IV)"
# test_entity = "http://dbkwik.webdatacommons.org/memory-alpha.wikia.com/resource/892-IV"
#%%
# subject_name = False
# cleaned_subj = ""
# attribute_dict = dict()
#
# for subj, pred, obj in g:
#     if str(subj) == test_entity:
#
#         if is_image_url(subj) or is_image_url(obj) or is_wikiPageWikiLink(pred) or is_wikiPageExternalLink(pred):
#             continue
#
#         if not subject_name:
#             cleaned_subj = clean_value(subj)
#             subject_name = True
#
#         cleaned_pred = clean_value(pred)
#         cleaned_obj  = clean_value(obj)
#
#         if cleaned_pred == "comment":
#             continue
#
#         if cleaned_pred in attribute_dict:
#             attribute_dict[cleaned_pred] = attribute_dict[cleaned_pred] + ", " + cleaned_obj
#         else:
#             attribute_dict[cleaned_pred] = cleaned_obj
#
# sorted_dict = {k: attribute_dict[k] for k in sorted(attribute_dict)}
# for k, v in sorted_dict.items():
#     print(f"- {k}: {v}")
#%%
attribute_dict = dict()

i = 0
for subj, pred, obj in tqdm(g):

    # i += 1
    # if i == 100:
    #     break
    if is_image_url(subj) or is_image_url(obj) or is_wikiPageWikiLink(pred) or is_wikiPageExternalLink(pred):
        continue

    cleaned_subj = clean_value(subj)
    str_subj = str(subj)
    cleaned_pred = clean_value(pred)
    cleaned_obj  = clean_value(obj)

    if cleaned_pred == "comment":
        continue

    if str_subj in attribute_dict:
        if cleaned_pred in attribute_dict[str_subj]:
            attribute_dict[str_subj][cleaned_pred].append(cleaned_obj)
        else:
            attribute_dict[str_subj][cleaned_pred] = [cleaned_obj]
    else:
        attribute_dict[str_subj] = dict()
        attribute_dict[str_subj][cleaned_pred] = [cleaned_obj]

sorted_dict = {k: attribute_dict[k] for k in sorted(attribute_dict)}

attribute_dict_sorted = dict()
for k, v in attribute_dict.items():
    attribute_dict_sorted[k] = {kk: v[kk] for kk in sorted(v)}
#%%
# attribute_dict_sorted["http://dbkwik.webdatacommons.org/stexpanded.wikia.com/resource/Magna_Roma"]
#%%
with open(output, "w") as json_file:
    json.dump(attribute_dict_sorted, json_file, indent=4)
#%%
