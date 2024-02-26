import hashlib
import os
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Code import ember
from Code.yara.predict_tree import *
from Code.yara.features import get_features
import lightgbm as lgb
from Code.yara import yaraparser as yp
import pefile
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__)) 
SAMPLE_FOLDER = CURRENT_FOLDER + "/x86_windows/"
ROOT_PATH = CURRENT_FOLDER
MODEL_PATH = CURRENT_FOLDER +"/Model/Model_LGB/model_v2.txt"
MODEL_YARA = CURRENT_FOLDER + "/Model/Model_Yara"
EXTRACT_FOLDER = CURRENT_FOLDER + "/x86_windows/" + "/extract/"

lstTree = []
print("Load model yara")
lstTree = load_tree(MODEL_YARA, 10)
print(f"Load model yara success, num tree = {len(lstTree)}")

if not os.path.exists(MODEL_PATH):
    print("Model {} does not exist".format(MODEL_PATH))
else:
    print("Load model AI")
    lgbm_model = lgb.Booster(model_file=MODEL_PATH)
def calculate_file_hash( file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()
def check_file_type(filename):
    try:
        pe = pefile.PE(filename)
        for clr_header in pe.OPTIONAL_HEADER.DATA_DIRECTORY:
            if clr_header.name == 'IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR':
                if clr_header.Size != 0:
                    return ".NET"
        return "C++"
    except Exception as e:
        print(e)
        return ""
def check_zip_file(filename):
    pass
def get_json_rule(raw_rule, name_rule):
    rule_json = {
        "header": "",
        "rule": {
            "name" : "",
            "meta" : "",
            "condition" : "",
            "rule_tree" : ""
        }
    }
    lst_rule_tree = []
    header = []
    try:
        raw_rule = raw_rule.replace("private ", "")
        rules = yp.ParsedYaraRules()
        rules.parse_yara_rules(raw_rule)

        for name, rule in rules.yara_rules.items():
            rule_tree = {
                "name": "",
                "string":"",
                "condition": ""
            }
            lst_string = []
            if rule.imports.imports != []:
                for lib_import in rule.imports.imports:
                    header.append(f"import {lib_import}")
            if name.find("tree") == 0:
                rule_tree["name"] = name
                strings = rule.strings.strings
                for s in strings:
                    lst_string.append({"#" + str(s) : strings[s].value })
                rule_tree["string"] = lst_string
                rule_tree["condition"] = rule.condition.raw_condition
                lst_rule_tree.append(rule_tree)
        rule_all = rules.yara_rules[name_rule]
        rule_json["header"] = header
        rule_json["rule"]["name"] = name_rule
        rule_json["rule"]["meta"] = {
            "author" : rule_all.meta.meta["author"][0].value,
            "description" : rule_all.meta.meta["description"][0].value,
            "date" : rule_all.meta.meta["date"][0].value
        }
        rule_json["rule"]["condition"] = rule_all.condition.raw_condition
        rule_json["rule"]["rule_tree"] = lst_rule_tree
    except Exception as e:
        print(e)
    return rule_json
def get_ai_scan_detection(file_path):
    dhash = calculate_file_hash(file_path)
    type = check_file_type(file_path)
    if type == "C++":
        global lgbm_model
        if lgbm_model == None:
            print("Load model AI")
            lgbm_model = lgb.Booster(model_file=MODEL_PATH)
        else:
            print("Model AI already exist")
        if not os.path.exists(file_path):
            print("errro")
        file_data = open(file_path, "rb").read()

        score = ember.predict_sample(lgbm_model, file_data, 2)
        iScore = int(score*100)
        print(f"Score file {file_path} is {score}")
        if score <= 0.5:
            typeSample = "benign"
            dangerous_degree = "Low"
        elif score <= 0.7:
            typeSample = 'malware'
            dangerous_degree = "Medium"
        elif score <= 0.9:
            typeSample = 'malware'
            dangerous_degree = "High"
        else:
            typeSample = 'malware'
            dangerous_degree = "Critical"
        if typeSample =='malware':
            return [{"positives": 1}]
        # summary_ai = {
        #     "AI_analysis_results": {
        #         "name" : "AI analysis results",
        #         "description": "Using machine learning to detect malware",
        #         "AI_detect" : typeSample,
        #         "score": iScore,
        #         "risk_level" : dangerous_degree
        #     },
        #     "YARA_rules":{
        #         "name" : "YARA rules",
        #         "description":	"Automatically generating YARA rules using AI model",
        #         "yaya_detect" : "benign"
        #     }
        # }
        # #Automatically generating YARA rules
        # global lstTree
        # if lstTree == []:
        #     print("Load model yara")
        #     load_tree(MODEL_YARA, 10)
        # else:
        #     print("Model yara already exist")
        # if score > 0.5:
        #     feature_detect = get_features(file_path)
        #     rule_name = "amas_" + str(dhash)
        #     rule, bRule = yararule_rf_predict(lstTree, rule_name, feature_detect, 0.5, 10)
        #     if bRule:
        #         summary_ai["YARA_rules"]["yaya_detect"] =  "malware"
        #     else:
        #         summary_ai["YARA_rules"]["yaya_detect"] =  "benign"
            
        #     #lấy json yara rule
        #     ruler_json = get_json_rule(rule, rule_name)
        #     print(ruler_json)
        # else:
        #     rule = ""
        #     ruler_json = {}
    return  [{"positives": 0}]
# file_path = "/tmp/AI_Malware/cve_2021_40444"
# res = get_ai_scan_detection(file_path)
# print(res[0]["positives"] == 0)
# file_path = "/tmp/AI_Malware/cve_2021_40444"
# res = get_ai_scan_detection(file_path)
# print(res[0]["positives"] == 0)
