def get_tp(golds, preds):
    tps = list()
    remaining = list()
    for pred in preds:
        found = False
        for gold in golds:
            if gold[0] == pred[0] and gold[1] == pred[1]:
                found = True
                tps.append(pred)
                break
        if found is False:
            remaining.append(pred)
    return tps, remaining


def get_fn(golds, preds):
    fns = list()
    for gold in golds:
        found = False
        for pred in preds:
            if gold[0] == pred[0] and gold[1] == pred[1]:
                found = True
                break
        if found is False:
            fns.append(gold)
    return fns


def get_fp(golds, preds):
    fps = list()
    remaining = list()
    for pred in preds:
        found = False
        for gold in golds:
            if (gold[0] == pred[0] and gold[1] != pred[1]) or (gold[0] != pred[0] and gold[1] == pred[1]):
                found = True
                fps.append(pred)
                break
        if found is False:
            remaining.append(pred)
    return fps, remaining


def discard_preds(preds, golds):
    gold1 = {element[0] for element in golds}
    gold2 = {element[1] for element in golds}

    returnables = list()
    for pair in preds:
        if pair[0] in gold1 or pair[1] in gold2:
            returnables.append(pair)
    return returnables


def evaluate_preds(golds, preds):
    return evaluate_preds_extended(golds, preds)[:3]


def evaluate_preds_extended_discard(golds, preds):
    preds_discarded = discard_preds(preds, golds)

    fns = get_fn(golds, preds_discarded)
    tps, remaining = get_tp(golds, preds_discarded)
    fps, remaining2 = get_fp(golds, remaining)

    precision = len(tps) / (len(tps) + len(fps))
    recall = len(tps) / (len(tps) + len(fns))
    f1 = 2 * precision * recall / (precision + recall)

    return precision, recall, f1, tps, fns, fps


def evaluate_preds_extended(golds, preds):
    fns = get_fn(golds, preds)
    tps, remaining = get_tp(golds, preds)
    fps, remaining2 = get_fp(golds, remaining)

    precision = len(tps) / (len(tps) + len(fps))
    recall = len(tps) / (len(tps) + len(fns))
    f1 = 2 * precision * recall / (precision + recall)

    return precision, recall, f1, tps, fns, fps

