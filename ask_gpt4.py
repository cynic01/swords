import os
import openai
from tqdm import tqdm
from eval import examples

openai.api_key = os.getenv("OPENAI_API_KEY")

example = examples[0]

for substitute, score in tqdm(example['substitutes']):
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "You are an evaluator helping to create accurate Lexical Substitution systems. Lexical Substitution is the task of finding appropriate substitutes for a target word in a context. You are ranking the ground truth list of candidates from the benchmark based on their contextual relevance for a given target. You will be given a text context, a target word, a substitute word, the target's part of speech tag, and a score from 0 to 100. As you gave out this score yourself, you will explain your reasoning behind this score. Let's think step-by-step for this problem."
        },
        {
            "role": "user",
            "content": f"context: {example['context']}\ntarget: {example['target']}\nsubstitute: {substitute}\ntarget_pos: {example['target_pos']}\nscore: {score}"
        }
    ],
    temperature=0.5,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    content = response["choices"][0]["message"]["content"]
    print(content)