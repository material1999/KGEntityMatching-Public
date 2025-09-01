import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input folder")
parser.add_argument("-o", "--output", help="Output folder")
args = parser.parse_args()

def get_type(element):
    try:
        return element.split("/")[4]
    except Exception as e:
        return ""
if not os.path.exists(args.output):
    os.makedirs(args.output)

files = os.listdir(args.input)

faulty = set()

for file in files:

    filename, extension = os.path.splitext(file)
    input_path = os.path.join(args.input, file)
    output_path = os.path.join(args.output, filename + ".json")

    with open(input_path, "r") as f:
        exact_match = json.load(f)

    exact_matches = list()
    
    for em in exact_match:
        first_type = get_type(em[0])
        second_type = get_type(em[1])
        if first_type == "" or second_type == "":
            if "wikia" in em[0] and "wikia" in em[1]:
                exact_matches.append(em)
            else:
                faulty.add(file)
                continue
        if first_type == second_type:
            exact_matches.append(em)

    exact_match_rightleft_dict = dict()
    for left, right, score in exact_matches:
        if right not in exact_match_rightleft_dict:
            exact_match_rightleft_dict[right] = (left, score)
        else:
            if score > exact_match_rightleft_dict[right][1]:
                exact_match_rightleft_dict[right] = (left, score)

    keep_exact_match = [[left, right, score] for right, (left, score) in exact_match_rightleft_dict.items()]

    exact_match_leftright_dict = dict()
    for left, right, score in keep_exact_match:
        if left not in exact_match_leftright_dict:
            exact_match_leftright_dict[left] = (right, score)
        else:
            if score > exact_match_leftright_dict[left][1]:
                exact_match_leftright_dict[left] = (right, score)

    keep_exact_match = [[left, right, score] for left, (right, score) in exact_match_leftright_dict.items()]

    with open(output_path, "w") as f:
        json.dump(keep_exact_match, f, indent=4)

print("FAULTY:", faulty)