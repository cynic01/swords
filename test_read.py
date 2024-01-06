from collections import defaultdict
import gzip
import json

# Load benchmark
with gzip.open('assets/parsed/swords-v1.1_test.json.gz', 'r') as f:
  swords = json.load(f)

# Gather substitutes by target
tid_to_sids = defaultdict(list)
for sid, substitute in swords['substitutes'].items():
  tid_to_sids[substitute['target_id']].append(sid)

# Iterate through targets
total_targets = 0
total_sentence_length = 0
for tid, target in swords['targets'].items():
  total_targets += 1
  context = swords['contexts'][target['context_id']]
  substitutes = [swords['substitutes'][sid] for sid in tid_to_sids[tid]]
  labels = [swords['substitute_labels'][sid] for sid in tid_to_sids[tid]]
  scores = [l.count('TRUE') / len(l) for l in labels]
#   print('-' * 80)
#   print(context['context'])
  total_sentence_length += len(context['context'].split())
#   print('-' * 20)
#   print('{} ({})'.format(target['target'], target['pos']))
#   print(', '.join(['{} ({}%)'.format(substitute['substitute'], round(score * 100)) for substitute, score in sorted(zip(substitutes, scores), key=lambda x: -x[1])]))
print(total_sentence_length)
print(total_targets)
print(total_sentence_length / total_targets)