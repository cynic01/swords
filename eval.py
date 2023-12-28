import os
import re
import gzip
import json
import random
import openai
import warnings
from tqdm import tqdm

with gzip.open('assets/parsed/swords-v1.1_dev.json.gz', 'r') as f:
  swords = json.load(f)

examples = [{'context': "Kim:\n\t\t\t\tI have completed the invoices for April, May and June and we owe\n\t\t\t\t\tPasadena each month for a total of $3,615,910.62. I am waiting to hear\n\t\t\t\t\tback from Patti on May and June to make sure they are okay with her.",
             'target': 'total',
             'target_offset': 105,
             'target_pos': "NOUN",
             'substitutes': [('amount', 80, 'The substitute word "amount" is a good fit in the given context as it also refers to a sum of money, similar to the target word "total". However, the word "total" also implies the result of an addition or accumulation of different amounts, which is crucial in this context as it\'s about the invoices for three different months. The substitute word "amount" doesn\'t convey this nuance as strongly, hence the score of 80 instead of a perfect 100.'), ('sum', 80, "The substitute word 'sum' is quite fitting in the given context as it can be used to refer to the total amount of money. Both 'total' and 'sum' are nouns that are commonly used in the context of accounting and finance to denote the aggregate amount. Therefore, the score of 80 is justified as 'sum' can be a good substitute for 'total' in this context. However, it's not a perfect 100 because 'total' is a more common term to use in this context to refer to the final amount of money, especially when referring to invoices and payments. 'Sum' might imply a process of adding up, which is slightly less fitting in this context than 'total'."), ('sum total', 60, 'The substitute "sum total" does fit into the context as it can be used to refer to the total amount of something. However, it is not as natural or as common of a usage as the word "total" in this context. The phrase "sum total" is often used in more formal or mathematical contexts, and may seem redundant or overly formal in everyday conversation or in this business context. Therefore, I gave it a score of 60, as it is somewhat suitable but not the ideal substitute.'), ('price', 60, 'The substitute word "price" can be used in place of "total" in this context, but it does not accurately convey the same meaning. The word "total" refers to the sum of all the amounts, while "price" generally refers to the cost of a single item or service. In this context, "price" could be interpreted as the cost of the invoices for each individual month, which is not the intended meaning. Therefore, the score is 60 because "price" is a somewhat relevant substitution, but it does not fully capture the meaning of "total" in this context.'), ('balance', 60, 'The substitute word "balance" can be used in a financial context to represent the amount of money. However, in the given context, the word "total" is used to refer to the sum of all the amounts for the three months. While "balance" could vaguely imply the same, it is not as precise as "total" because balance usually refers to an amount left over after deductions, not a sum of amounts. Therefore, the score is 60, indicating that while the substitute word "balance" can fit in the context, it is not the most accurate replacement for "total".'), ('gross', 60, "The substitute word 'gross' can be used in the context, but it may not convey the exact meaning as 'total'. The term 'gross' often refers to the total amount of something before deductions, so it could imply that there may be further deductions from the amount of $3,615,910.62. This may not be what the original sentence is implying as 'total' often refers to the final or complete sum. Therefore, while 'gross' could somewhat fit in the context, it may slightly alter the meaning, hence the score of 60."), ('figure', 50, 'The substitute word "figure" is somewhat contextually relevant to the target word "total" in this context. Both words can be used to refer to a numerical value or sum, which is why it has been given a moderate score of 50. However, "figure" is not as precise as "total" in this context, as "total" directly implies the sum of all amounts, while "figure" could also refer to a single amount. Therefore, while the word "figure" could potentially work in this context, it does not convey the meaning as accurately as the target word "total".'), ('cost', 50, "The substitute word 'cost' is somewhat relevant in the given context. The context is about the completion of invoices for certain months and the amount owed to Pasadena, which can be considered as a 'cost'. However, the target word 'total' is more specific to the context, referring to the cumulative amount for the specified months. The substitute word 'cost' lacks this specificity, hence it only gets a score of 50. It fits the context but doesn't convey the exact meaning as 'total' does."), ('full amount', 40, 'The substitute "full amount" is partially correct in this context, which is why it received a score of 40. The word "total" in the given context refers to the summation of the amounts owed for the months of April, May, and June. The phrase "full amount" can be interpreted as the complete sum that is owed, so it carries a similar meaning. However, "full amount" might also imply the entirety of a single payment, not necessarily a summation of several smaller amounts. Therefore, while it\'s not entirely out of place, it\'s not the most accurate substitution for "total" in this specific context.'), ('whole', 30, "The substitute word 'whole' is not entirely incorrect in this context, but it doesn't fit as well as the target word 'total'. The word 'total' is commonly used in financial contexts to refer to the sum of multiple amounts, as it is used here. On the other hand, 'whole' can also mean the sum of all parts, but it's not typically used in financial contexts. Instead, it's often used to refer to something that is complete or undivided. Therefore, while 'whole' could potentially work in this context, it's not the best fit, which is why I gave it a score of 30.")]}]

def random_generate(
    context,
    target,
    target_offset,
    target_pos=None):
  """Produces _substitutes_ for _target_ span within _context_

  Args:
    context: A text context, e.g. "My favorite thing about her is her straightforward honesty.".
    target: The target word, e.g. "straightforward"
    target_offset: The character offset of the target word in context, e.g. 35
    target_pos: The UD part-of-speech (https://universaldependencies.org/u/pos/) for the target, e.g. "ADJ"

  Returns:
    A list of substitutes and scores e.g. [(sincere, 80.), (genuine, 80.), (frank, 70), ...]
  """
  # TODO: Your method here; placeholder outputs 10 common verbs
  substitutes = ['be', 'have', 'do', 'say', 'get', 'make', 'go', 'know', 'take', 'see']
  scores = [random.random() for _ in substitutes]
  return list(zip(substitutes, scores))

def gpt4_generate(
    context,
    target,
    target_offset,
    target_pos=None,
    shots=0):
    """Produces _substitutes_ for _target_ span within _context_

    Args:
        context: A text context, e.g. "My favorite thing about her is her straightforward honesty.".
        target: The target word, e.g. "straightforward"
        target_offset: The character offset of the target word in context, e.g. 35
        target_pos: The UD part-of-speech (https://universaldependencies.org/u/pos/) for the target, e.g. "ADJ"

    Returns:
        A list of substitutes and scores e.g. [(sincere, 80.), (genuine, 80.), (frank, 70), ...]
    """
    if len(examples) < shots:
      print(f"Not enough examples for {shots}-shot prompting")
      exit(1)

    messages = [{
      "role": "system",
      "content": "You are an evaluator helping to create accurate Lexical Substitution systems. Lexical Substitution is the task of finding appropriate substitutes for a target word in a context.  You will be given a text context, a target word, and the target's part of speech tag. You will output a ranked list of 10 substitute candidate words for the given target word and give a score for each substitute candidate word from 0 to 100."
    }]

    format_content = lambda context_i, target_i, target_pos_i: f"context: {context_i}\ntarget: {target_i}\ntarget_pos: {target_pos_i}"
    format_prompt = "\n\nOutput your answer in the format of \"Ranking number. Reason: [your reason]. Candidate: [your candidate word]. Score: [your score].\" Let's think step-by-step for this problem by giving a reason."

    for i in range(shots):
      example = [
        {
          "role": "user",
          "content": format_content(examples[i]['context'], examples[i]['target'], examples[i]['target_pos']) + format_prompt if i == 0 else format_content(examples[i]['context'], examples[i]['target'], examples[i]['target_pos'])
        },
        {
          "role": "assistant",
          "content": "\n\n".join(f"{idx+1}. Reason: {reason} Candidate: {candidate}. Score: {score}." for idx, (candidate, score, reason) in enumerate(examples[i]['substitutes']))
        }
      ]
      messages.extend(example)
    
    messages.append(
      {
        "role": "user",
        "content": format_content(context, target, target_pos) + format_prompt if shots == 0 else format_content(context, target, target_pos)
      }
    )
    # print("Message:")
    # print(messages)

    # get response from GPT-4
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    content = response["choices"][0]["message"]["content"]
    # print("Response:")
    # print(content)

    # parse response content
    substitutes = re.findall(r'[Cc]andidate: (.*?)[.,;]', content)
    scores = re.findall(r'[Ss]core: (.*?)[.,;\s]', content)
    scores = [int(score) for score in scores]
    return list(zip(substitutes, scores))

if __name__ == '__main__':
  # NOTE: 'substitutes_lemmatized' should be True if your method produces lemmas (e.g. "run") or False if your method produces wordforms (e.g. "ran")
  result = {'substitutes_lemmatized': True, 'substitutes': {}}
  errors = 0
  for tid, target in tqdm(swords['targets'].items()):
    context = swords['contexts'][target['context_id']]
    try:
      result['substitutes'][tid] = gpt4_generate(
          context['context'],
          target['target'],
          target['offset'],
          target_pos=target.get('pos'),
          shots=1)
    except:
      errors += 1
      continue

  if errors > 0:
      warnings.warn(f'{errors} targets were not evaluated due to errors')

  with open('swords-v1.1_dev_gpt4_1shot.lsr.json', 'w') as f:
    f.write(json.dumps(result, indent=4))