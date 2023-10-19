import openai
import json
import os
import sys
from tqdm import tqdm
import pandas as pd


score_mode = sys.argv[1]   ##'normal' or 'exam'
QUES_TYPES = ['MCQ','MCQ(multiple)','Integer','Numeric','Integer(unbounded-positive)']

def compute_metric(gold, resp, question_type):
    # print(gold, resp)
    if "MCQ" in question_type:
        g = [c for c in ['A', 'B', 'C', 'D'] if c in gold]
        r = [c for c in ['A', 'B', 'C', 'D'] if c in resp]
        if len(set(r)) == 0:
            return 0.0
        prec = len(set(g).intersection(set(r)))/len(set(r))
        rec = len(set(g).intersection(set(r)))/len(set(g))
        if prec + rec == 0:
            f1 = 0
        else:
            f1 = 2*prec*rec/(prec+rec)
        return f1
    else:
        if resp == "None":
            return 0.0
        g = float(gold)
        r = float(resp)
        if abs(g-r) < 0.1:
            return 1.0
        else:
            return 0.0


def compute_max_score(question_type,year):

    if question_type == 'MCQ(multiple)':
        return 4
    elif question_type == 'MCQ':

        return 3 
    elif question_type == 'Integer' or question_type == 'Integer(unbounded-positive)':

        return 3 
    elif question_type == 'Numeric':

        if year == 2020:
            return 4 
        elif year == 2021:
            return 2 
        else:
            return 3 
        
    else:
        print(f"Error in question type {question_type}")


def compute_exam_score(gold, resp, question_type, year):

    year = int(year.split(' ')[2])

    if question_type == 'MCQ(multiple)':
        for r in resp.strip():

            if r == 'None':
                return 0
            cnt = 0
            for r in resp.strip():
                if not r in gold.strip():
                    return -2
                cnt = cnt + 1

            assert (cnt <= len(gold.strip()))

            if cnt == len(gold.strip()):
                return 4
            else:
                return cnt

    elif question_type == 'MCQ':
        pos = 3
        neg = -1

    elif question_type == 'Integer':
        pos = 3
        neg = 0
        if year >= 2020:
            neg = -1

    elif question_type == 'Numeric':
        pos = 3
        neg = 0
        if year == 2020:
            pos = 4
        if year == 2021:
            pos = 2
    else:
        print(f"Error in question type {question_type}")

    if compute_metric(gold, resp, question_type) == 1.0:
        return pos
    else:
        return neg


def compute_normal_score(gold, resp, question_type, year):

    assert question_type in QUES_TYPES

    if question_type == 'MCQ(multiple)':
        gold = set(gold.strip())
        resp = set(resp.strip())
        if resp == gold :
            return 1.0
        else: 
            return 0.0 
    else:
        return compute_metric(gold,resp,question_type)



# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.Model.list()
responses = json.load(open("responses.json"))

extractor_model = 'text-davinci-003'
models = ["GPT3", "GPT3_CoT_exam", "GPT3.5","GPT3.5_exam", "GPT4",  "GPT4_exam"]
models = ["random", "GPT3_CoT_exam","GPT3.5_exam",  "GPT4_exam"]

output = []
for response in responses:

    if response["finalized"]:
        if response['description'] not in ['JEE Adv 2021 Paper 1', 'JEE Adv 2021 Paper 2', 'JEE Adv 2022 Paper 1', 'JEE Adv 2022 Paper 2']:
            continue
        out = {}
        out["question_type"] = response["question_type"]
        out["index"] = response["index"]
        out["year"] = response["description"]
        out["subject"] = response["subject"]
        gold = response["gold"]
        out["gold"] = gold
        if response["question_type"] == "MCQ":
            out["random_score"] = 0.25
        elif response["question_type"] == "MCQ(multiple)":
            out["random_score"] = 0.0625
        elif response["question_type"] == "Integer":
            out["random_score"] = 0.1
        else:
            out["random_score"] = 0
            
        for model in models:
            if model == "random":
                continue
            resp = response[f"{model}_extract"]
            out[f"{model}_response"] = resp

            resp = response[f"{model}_extract"]
            out[f"{model}_response"] = resp
            if score_mode == 'normal':
                # print(out)
                out[f'{model}_score'] = compute_normal_score(gold,resp,out["question_type"],out["year"])
            else:
                out[f'{model}_score'] = compute_exam_score(gold,resp,out["question_type"],out["year"])
            out[f'max_score'] = compute_max_score(out["question_type"],out["year"])

        output.append(out)

df = pd.DataFrame()
df['question_type'] = [x['question_type'] for x in output]
df['index'] = [x['index'] for x in output]
df['year'] = [x['year'] for x in output]
df['subject'] = [x['subject'] for x in output]
df['gold'] = [x['gold'] for x in output]
df['random_score'] = [x['random_score'] for x in output]
for model in models:
    df[f"{model}_response"] = [
        x.get(f"{model}_response", "None") for x in output]
    df[f"{model}_score"] = [x.get(f"{model}_score", 0) for x in output]



df.to_csv(f"scores_{score_mode}.csv", index=False)


if sys.argv[2] == 'year_wise':
    col_dict = {}
    for model in models:
        if score_mode == 'exam':
            col_dict[f'{model}_score'] = ['sum']
        else:
            col_dict[f'{model}_score'] = ['mean']

    col_dict[f'{models[0]}_score'].insert(0,'count')

    grouped_multiple = df.groupby(['year']).agg(col_dict)
    grouped_multiple.columns = ['count'] + models
    grouped_multiple = grouped_multiple.reset_index()
    grouped_multiple = grouped_multiple.round(3)
    grouped_multiple.to_csv(f"aggregated_scores_{score_mode}_{sys.argv[2]}.csv", index=False)
else:
    col_dict = {}
    for model in models:
        if score_mode == 'exam':
            col_dict[f'{model}_score'] = ['sum']
        else:
            col_dict[f'{model}_score'] = ['mean']

    col_dict[f'{models[0]}_score'].insert(0,'count')

    grouped_multiple = df.groupby(['subject']).agg(col_dict)
    grouped_multiple.columns = ['count'] + models
    grouped_multiple = grouped_multiple.reset_index()
    grouped_multiple = grouped_multiple.round(3)
    grouped_multiple.to_csv(f"aggregated_scores_{score_mode}_{sys.argv[2]}.csv", index=False)