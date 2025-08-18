import json
import torch
from sentence_transformers import util
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import argparse
import os
from utils.loaders import gold_folder_path
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dogtags", help="Dogtags folder name")
parser.add_argument("-e", "--embeddings", help="Embeddings folder name")
parser.add_argument("-o", "--output", help="Output folder")
parser.add_argument("-g", '--gpu', action='store_true', help='gpu or cpu')
parser.add_argument("-k", "--topk", type=int, default=100, help="TopK pairs to select for reranker")
parser.add_argument("-m", "--model", default="BAAI/bge-reranker-large", help="Model name")

args = parser.parse_args()


if not os.path.exists(args.output):
    os.makedirs(args.output)

golds = os.listdir(gold_folder_path)
device = torch.device('cuda' if args.gpu and torch.cuda.is_available() else 'cpu')

output_container = dict()
res_container_backward = dict()

print("Output path:", args.output)

for gold in golds:
    print(gold)
    gold_cleand = gold.split(".")[0]

    g1, g2 = gold_cleand.split("-")

    with open(os.path.join(args.embeddings, g1 + ".json"), "r") as f:
        g1_embeddings = json.load(f)

    with open(os.path.join(args.embeddings, g2 + ".json"), "r") as f:
        g2_embeddings = json.load(f)

    with open(os.path.join(args.dogtags, g1 + ".json"), "r") as f:
        g1_dogtags = json.load(f)

    with open(os.path.join(args.dogtags, g2 + ".json"), "r") as f:
        g2_dogtags = json.load(f)

    g1_embeddings_list = list(g1_embeddings.values())
    g1_ids_list = list(g1_embeddings.keys())

    g2_embeddings_list = list(g2_embeddings.values())
    g2_ids_list = list(g2_embeddings.keys())

    tensor_small = torch.Tensor(g1_embeddings_list).to(device)
    tensor_big = torch.Tensor(g2_embeddings_list).to(device)
    node_order = util.semantic_search(tensor_small, tensor_big, top_k=args.topk)

    top_dict = dict()
    for idx, (node_id, order) in enumerate(zip(g1_ids_list, node_order)):
        items_list = list()
        for item in order:
            items_list.append((g2_ids_list[item['corpus_id']], item['score']))
        top_dict[node_id] = items_list

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model)
    model.to(device)
    model.eval()

    output_pairs = list()
    for node in tqdm(g1_ids_list):
        reranker_input = list()
        id_list = list()
        for element in top_dict[node]:
            id_list.append(element[0])
            reranker_input.append(
                [
                    str(g1_dogtags[node]),
                    str(g2_dogtags[element[0]])
                ]
            )

        with torch.no_grad():
            inputs = tokenizer(reranker_input, padding=True, truncation=True, return_tensors='pt', max_length=512).to(
                device)
            scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
            # print(scores)

        max_index = torch.argmax(scores)
        max_index_int = int(max_index.item())
        max_value = scores[max_index]
        max_value_float = float(max_value.item())
        output_pairs.append([node, id_list[max_index_int], max_value_float])

    with open(os.path.join(args.output, gold_cleand+".json"), "w") as f:
        json.dump(output_pairs, f)
