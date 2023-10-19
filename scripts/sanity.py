import json
import numpy as np

qs = json.load(open('responses.json'))
# Check 1
for q in qs:
    if q['finalized'] and q['question_type'] == 'MCQ':
        if q['gold'] not in ["A", "B", "C", "D"]:
            print(q, "\n\n")

# Check 2
for q in qs:
    if q['finalized'] and q['question_type'] == 'MCQ(multiple)':
        for x in q['gold']:
            if x not in ["A", "B", "C", "D"]:
                print(q, "\n\n")
                break
# Check 3
for q in qs:
    if q['finalized'] and q['question_type'] == 'Integer':
        for x in q['gold']:
            if int(x) not in [0,1,2,3,4,5,6,7,8,9]:
                print(q)
# Check 4
for q in qs:
    if q['finalized'] and q['question_type'] == 'Numeric':
        try:
            y = float(q['gold'])
        except:
            print(q)

# Check 5
print(np.unique([q['question_type'] for q in qs]))
assert len(np.unique([q['question_type'] for q in qs])) == 4

# Check 6
for q in qs:
    if q['finalized'] and q['question_type'] in ['Numeric', 'Integer']:
        good = False
        for c in ['A', 'B', 'C', 'D']:
            if c not in q['question_edited']:
                good = True
        # if not good:
        #     print(q, "\n\n")

# Check 7
error = False
for q in qs:
    if q['finalized']:
        if q['question_type'] in ['Numeric', 'Integer']:
            for key in ['gold', 'GPT3_extract', 'GPT3.5_extract', 'GPT4_extract']:
                try:
                    if q[key] == "None":
                        continue
                    float(q[key])
                except:
                    breakpoint()
        if q['question_type'] in ['MCQ', 'MCQ(multiple)']:
            for key in ['gold', 'GPT3_extract', 'GPT3.5_extract', 'GPT4_extract']:
                if q[key] == "None":
                    continue
                for x in q[key]:
                    if x not in ['A', 'B', 'C', 'D']:
                        error = True
            if error:
                breakpoint()
                error = False
        if q['question_type'] == 'MCQ':
            for key in ['gold', 'GPT3_extract', 'GPT3.5_extract', 'GPT4_extract']:
                if len(q[key]) > 1 and q[key] != "None":
                    breakpoint()
                