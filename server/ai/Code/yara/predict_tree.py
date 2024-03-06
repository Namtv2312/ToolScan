#!/usr/bin/python

import pickle
import numpy as np
import networkx
import json
import itertools
from networkx.drawing.nx_pydot import write_dot
from networkx.algorithms.shortest_paths.generic import shortest_path
from datetime import datetime
import joblib
import os

iCount = 0
string_symbol_cache = {}

def tree_predict(rulename, idTree, treegraph,  feature_detect):
    root_node = list(networkx.topological_sort(treegraph))[0]
    stringset = set()
    feature_detect = feature_detect
    yara_paths = []

    # build tree logic recursively
    def recurse(n1,depth=0):
        global iCount
        iCount = 0
        descendants = treegraph.successors(n1)
        tab = ""#*depth
        or_strings = []
        for n2 in descendants:
            condition = treegraph.get_edge_data(n1,n2)['split_type']
            threshold = treegraph.get_edge_data(n1,n2)['threshold']
            test = treegraph.nodes(data=True)
            n1fname = treegraph.nodes(data=True)[n1]['fname']
            #n1fname = treegraph.nodes(data=True)[n1][1]['fname']
            feature_type = None
            if n1fname not in feature_detect:
                feature_detect[n1fname] = 0.0
            if feature_detect[n1fname] <= threshold:
                con_ = "false"
            else:
                con_ = "true"
            if condition != con_:
                continue
            if n1fname.startswith("$"):
                feature_type = "string"
                if n1fname in string_symbol_cache:
                    nodesymbol = string_symbol_cache[n1fname]
                else:
                    nodesymbol = "#s{0}{1}".format(idTree, n1)        #n1)
                    iCount += 1
                    string_symbol_cache[n1fname] = nodesymbol
                stringset.add((nodesymbol,n1fname[1:]))
            elif n1fname.startswith("@"):
                feature_type = "special"
                nodesymbol = "{0}".format(n1fname[1:])
            else:
                raise Exception("Unknown feature type")
            yara_paths.append(n2)
            if condition == 'false':
                yara_condition = "({0} <= {1})".format(nodesymbol,threshold)
            else:
                yara_condition = "({0} > {1})".format(nodesymbol,threshold)
            descendant, yara_path = recurse(n2,depth+1)
                
           
            if descendant:
                or_strings.append((yara_condition, descendant))
            else:
                or_strings.append((yara_condition, None))

        retstrings = []
        for idx, (yara_condition,descendant) in enumerate(or_strings):
            if yara_condition and descendant:
                retstrings.append(tab+yara_condition+"\n"+" and "+descendant)
            elif yara_condition:
                retstrings.append(tab+yara_condition+"\n")

        if len(retstrings):
            retstring = "("+" or ".join(retstrings)+")"
        else:
            retstring = None
        return retstring, yara_paths

    conditiondata, yara_paths = recurse(root_node)
    nodes = treegraph.nodes()._nodes
    
    if conditiondata is None:
        return ""
    test = nodes[yara_paths[len(yara_paths)-1]]
    if "malware_prob" not in nodes[yara_paths[len(yara_paths)-1]]:
        return ""

    template = """
private rule %s
{
    strings:
%s

    condition:
%s
}
"""
    sorted_strings = sorted(list(stringset),key=lambda x:int(x[0][2:].split()[0]))
    stringdata = "\n".join(["\t\t{0} = {1} fullword".format(i.replace("#","$"),json.dumps(j)) for i,j in sorted_strings])
    ####
    if stringdata == "":
        template = """
private rule %s
{
    condition:
%s
}
"""
        rule = template % (rulename,conditiondata)
    else:
        rule = template % (rulename,stringdata,conditiondata)
    return rule

def load_tree(foldelTree, numTree):
    lstTree = []
    try:
        for i in range(numTree):
            tree = joblib.load(os.path.join(foldelTree, f"tree{i}.pkl"))
            lstTree.append(tree)
    except Exception as e:
        print(e)
    return lstTree
def yararule_rf_predict(lstTree, rulename, feateres_detect, percent_match_threshold=0.9,numTree = 10):

    rulelist = []
    names = []
    #lstTree = []
    if len(lstTree) != numTree:
        print(f"number tree != {numTree}")
        return "", False
    for i,tree in enumerate(lstTree):
        rule = ""
        rule = tree_predict(f"tree{i}", i, tree, feateres_detect)
        if rule != "":
            names.append(f"tree{i}")
            rulelist.append(rule)
    # for i in range(numTree):
    #     tree = joblib.load(os.path.join(folderPathTree, f"tree{i}.pkl"))
    #     #lstTree.append(tree)
    #     rule = ""
    #     rule = tree_predict(f"tree{i}", i, tree, feateres_detect)
    #     if rule != "":
    #         names.append(f"tree{i}")
    #         rulelist.append(rule)
    if len(names) < int(numTree * percent_match_threshold):
        print("[no detect]")
        return "", False
    rule = "\n\n".join(rulelist)
    rule += "\n\n"

    rule = 'import "math"\n' + rule
    if "pe." in rule:
        rule = 'import "pe"\n' + rule

    template = """
rule %s
{
    meta:
        author = "Amas"
        description = "Automatically generating YARA rules using model AI"
        date = "%s"
    condition:
%s
}
    """
    combination_size = int(numTree * percent_match_threshold)
    #combination_size = len(estimator.estimators_) - 1
    conditions = []
    for combination in itertools.combinations(names, combination_size):
        condition = "("+" and ".join(combination)+")"
        conditions.append(condition)
    conditiondata = "\t"+"\n\t\t or ".join(conditions)

    rule += template % (rulename,str(datetime.now().strftime("%Y-%m-%d %H:%M:%S") ), conditiondata)
    print("[ncs detect]")
    #open(rulename +".yara","w+").write(rule)
    return rule, True