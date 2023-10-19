#Usage: python3 api_call.py 2022
import sys
import os
from tqdm import tqdm
from requests import HTTPError
import copy
import json
import os,sys
import openai
import pandas as pd
from requests import HTTPError 
from tqdm import tqdm 
import argparse 
 
prompt_library = {
    "JEE Adv 2016": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Integer": "In this question, the answer is an integer between 0 and 9, both inclusive. For the right answer, you will get +3 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
    "JEE Adv 2017": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Integer": "In this question, the answer is an integer between 0 and 9, both inclusive. For the right answer, you will get +3 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
    "JEE Adv 2018": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Numeric": "In this question, the answer will be a numeric value. Give the numerical answer correct upto the 2nd decimal digit. For the right answer, you will get +3 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
    "JEE Adv 2019": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Numeric": "In this question, the answer will be a numeric value. Give the numerical answer correct upto the 2nd decimal digit. For the right answer, you will get +3 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
    "JEE Adv 2020": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Integer": "In this question, the answer is an integer between 0 and 9, both inclusive. For the right answer, you will get +3 marks and -1 marks for the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "Numeric": "In this question, the answer will be a numeric value. Give the numerical answer correct upto the 2nd decimal digit. For the right answer, you will get +4 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
    "JEE Adv 2021": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Numeric": "In this question, the answer will be a numeric value. Give the numerical answer correct upto the 2nd decimal digit. For the right answer, you will get +2 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
        "Integer(unbounded-positive)": "In this question, the answer is a positive integer. For the right answer, you will get +4 marks and 0 marks for the wrong answer. If you decide to not attempt, you will get 0 marks.",

    },
    "JEE Adv 2022": {
        "MCQ": "In this question, only one option is correct. For the right answer, you will get +3 marks and -1 if you give the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "MCQ(multiple)": "In this question, multiple options can be correct. If all correct options are selected, you will get +4 marks. If any wrong option is selected, you will get -2 marks. If all correct options are not selected, but some of them are selected, and none of the wrong options are selected, you will get +1 marks for each correct option. If you decide to not attempt, you will get 0 marks.",
        "Integer": "In this question, the answer is an integer between 0 and 9, both inclusive. For the right answer, you will get +3 marks and -1 marks for the wrong answer. If you decide to not attempt, you will get 0 marks.",
        "Numeric": "In this question, the answer will be a numeric value. Give the numerical answer correct upto the 2nd decimal digit. For the right answer, you will get +3 marks. There is no negative marking. If you decide to not attempt, you will get 0 marks.",
    },
}


def main():
    prompt_mode = sys.argv[1]
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.Model.list()

    # models = ["text-davinci-003", "gpt-3.5-turbo", "gpt-4"]
    models = ["text-davinci-003", "gpt-3.5-turbo"]
    models = ["text-davinci-003"]
    # models = ["gpt-3.5-turbo"]
    # models = ["gpt-4"]

    model_nickname = {
        "text-davinci-003": "GPT3",
        "gpt-3.5-turbo": "GPT3.5",
        "gpt-4": "GPT4"
    }

    questions = json.load(open("responses_old.json"))

    num_retries = 0
    MAX_RETRIES = 10

    for question in tqdm(questions):
        response_dict = copy.deepcopy(question)
        ques = question["question_edited"]
        stripped_ques = ques.replace("\n\n", "\n").strip()
        print('############# QUESTION: ',
              question['description'], '####################')
        # breakpoint()
        if os.path.exists('responses.json'):
            with open('responses.json', 'r') as infile:
                responses = json.load(infile)
                found = False

                for i, old_resp in enumerate(responses):
                    if old_resp['description'] == question['description'] and old_resp['index'] == question['index']:
                        found = all([old_resp.get(
                            f"{model_nickname[model]}_{prompt_mode}_response", False) for model in models])
                        break
                # breakpoint()
                if found:
                    print("This question has already been done")
                    continue

        if question['finalized']:
            for model in models:
                print('################### MODEL: ',
                      model, '####################')
                prefix_prompt = ""
                suffix_prompt = ""
                if prompt_mode == "original":
                    if question['question_type'] == 'Integer':
                        prefix_prompt = "Give an answer in the form of an integer between 0 and 9.\n\n"
                    if question['question_type'] == 'Numeric':
                        prefix_prompt = "Give an answer in the form of a decimal number with 2 digits after the decimal point.\n\n"
                elif prompt_mode == "exam":
                    exam = question['description'][:question['description'].index(
                        "Paper")].strip()
                    prefix_prompt = f'{prompt_library[exam][question["question_type"]]} Try to get as many marks as possible.\n'
                elif prompt_mode == "CoT_exam":
                    exam = question['description'][:question['description'].index(
                        "Paper")].strip()
                    prefix_prompt = f'{prompt_library[exam][question["question_type"]]} Try to get as many marks as possible.\n'
                    suffix_prompt = "\nLet's think step by step."

                prompt = prefix_prompt + stripped_ques + suffix_prompt
                prompt = prompt.strip()
                response_dict[f"prompt_{prompt_mode}"] = prompt
                print("Prompt:")
                print(prompt)
                #call openai API
                # breakpoint()
                while True:
                    try:
                        if model == "text-davinci-003":
                            response = openai.Completion.create(
                                model=model,
                                prompt=prompt,
                                max_tokens=2048,
                                temperature=0
                            )
                        else:
                            response = openai.ChatCompletion.create(
                                model=model,
                                messages=[
                                    {"role": "system", "content": "You are giving an exam. Be concise and try your best. End your response with the final answer."},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=2048,
                                temperature=0
                            )
                        break
                    except HTTPError:
                        num_retries += 1
                        print("Failure, retrying!")
                        if num_retries >= MAX_RETRIES:
                            exit()

                response_dict[f"{model_nickname[model]}_{prompt_mode}_response"] = response

        responses = []

        if os.path.exists('responses.json'):
            with open('responses.json', 'r') as infile:
                responses = json.load(infile)
        found = False
        for i, old_resp in enumerate(responses):
            if old_resp['description'] == question['description'] and old_resp['index'] == question['index']:
                for model in models:
                    responses[i][f"{model_nickname[model]}_{prompt_mode}_response"] = response_dict[
                        f"{model_nickname[model]}_{prompt_mode}_response"]
                found = True
                break

        if not found:
            responses.append(response_dict)

        json.dump(responses, open('responses.json', 'w'), indent=4)


if __name__ == '__main__':
    main()
