import json
import pandas as pd
from sklearn.model_selection import train_test_split

if __name__ == '__main__':
    with open('../../expt_results/pre_tweet/responses.json') as responses:
        in_dicts = json.load(responses)
        X_y = {"response": [], "extract": []}
        for in_dict in in_dicts:
            if in_dict['finalized']:
                for key in ["GPT3_CoT", "GPT3.5", "GPT4"]:
                    if key == "GPT3_CoT":
                        X_y["response"].append(in_dict[f'{key}_exam_response']['choices'][0]['text'])
                        X_y["extract"].append(in_dict[f'{key}_exam_extract'])
                    else:
                        X_y["response"].append(in_dict[f'{key}_exam_response']['choices'][0]['message']['content'])
                        X_y["extract"].append(in_dict[f'{key}_exam_extract'])
                for key in ["GPT3", "GPT3.5", "GPT4"]:
                    if f'{key}_response' in in_dict and f'{key}_extract' in in_dict:
                        # breakpoint()
                        try:
                            if in_dict[f'{key}_response'] == "":
                                continue
                            if key == "GPT3":
                                X_y["response"].append(in_dict[f'{key}_response']['choices'][0]['text'])
                                X_y["extract"].append(in_dict[f'{key}_extract'])
                            else:
                                X_y["response"].append(in_dict[f'{key}_response']['choices'][0]['message']['content'])
                                X_y["extract"].append(in_dict[f'{key}_extract'])
                        except:
                            breakpoint()
                    
        X_y = pd.DataFrame(X_y)
        train_df = X_y.sample(n=len(X_y)-50)
        val_df = X_y.drop(train_df.index)
        print("Training data:", len(train_df), "Validation data:", len(val_df))
        pd.DataFrame(train_df).to_csv('data/extractor_dataset_train.csv', index=False)
        pd.DataFrame(val_df).to_csv('data/extractor_dataset_val.csv', index=False)