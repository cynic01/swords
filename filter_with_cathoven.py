from collections import defaultdict
from tqdm import tqdm
import os
import gzip
import json
import requests

def get_cefr_level(original_context, target_word):
    '''
    Get the CEFR level of the target word in the original context
    '''

    data = {
        'client_id': os.getenv("CATHOVEN_CLIENT_ID"),
        'client_secret': os.getenv("CATHOVEN_CLIENT_SECRET"),
        'keep_min': "true",  # Replace value with the actual value
        'return_final_levels': "true",  # Replace value with the actual value
        'text': original_context,
        'return_sentences': "true"  # Replace value with the actual value
    }

    try:
        response = requests.post('https://enterpriseapi.cathoven.com/cefr/process_text', json=data)
        response.raise_for_status()
        responseData = response.json()

        # find the index of the target word in the response
        word_index = None
        contain_more_than_one_sentence = False
        sentence_index = None  # the sentence that contains the target word
        # detect if original context contains more than one sentence
        if len(responseData['sentences']) > 1:
            contain_more_than_one_sentence = True
            for sid, obj in responseData['sentences'].items():
                if target_word in obj['word']:
                    words = obj['word']
                    word_index = [i for i, word in enumerate(words) if target_word == word]
                    sentence_index = sid
                    break
        else:
            words = responseData['sentences']['0']['word']
            word_index = [i for i, word in enumerate(words) if target_word == word]
        
        if word_index:
            t_word_index = word_index[0]  
            if contain_more_than_one_sentence and sentence_index:
                cefr_level = responseData['sentences'][sentence_index]['CEFR'][t_word_index]
            else:
                cefr_level = responseData['sentences']['0']['CEFR'][t_word_index]
        else:
            print("WARNING: Target word {} does not exist in the context sentence".format(target_word))
            print("Original context: {}".format(original_context))
            cefr_level = None
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        cefr_level = None
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        cefr_level = None
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        cefr_level = None
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        cefr_level = None
    except Exception as e:
        print(e)
        cefr_level = None

    return cefr_level

# Load benchmark
with gzip.open('assets/parsed/swords-v1.1_dev.json.gz', 'r') as f:
  swords = json.load(f)

# Gather substitutes by target
tid_to_sids = defaultdict(list)
for sid, substitute in swords['substitutes'].items():
  tid_to_sids[substitute['target_id']].append(sid)

# Iterate through targets
out = []
count = 0
for tid, target in tqdm(swords['targets'].items()):
  if count == 5: break  # REMOVE THIS LINE TO FILTER WHOLE DATASET
  if ' ' in target['target']:
    continue
  context = swords['contexts'][target['context_id']]
  target_cefr = get_cefr_level(context['context'], target['target'])
  substitutes = [swords['substitutes'][sid] for sid in tid_to_sids[tid]]
  labels = [swords['substitute_labels'][sid] for sid in tid_to_sids[tid]]
  scores = [l.count('TRUE') / len(l) for l in labels]
  all_substitutes = []
  for substitute, score in sorted(zip(substitutes, scores), key=lambda x: -x[1]):
    if score < 0.5:
      continue
    cefr = get_cefr_level(context['context'].replace(target['target'], substitute['substitute']), substitute['substitute'])
    if cefr is not None and cefr < target_cefr:
       continue
    all_substitutes.append({'substitute': substitute['substitute'], 'score': round(score * 100), 'cefr': cefr})
  out.append({'context': context['context'],
              'target': target['target'],
              'target_pos': target['pos'],
              'target_cefr': target_cefr,
              'substitutes': all_substitutes})
  with open('swords_filtered.json', 'w') as fout:
    json.dump(out, fout, ensure_ascii=False, indent=2)
  count += 1
  