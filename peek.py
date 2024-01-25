import json

with open(f'swords-v1.1_dev_filtered.json') as f:
    swords = json.load(f)

total_targets = 0
total_target_cefr = 0
total_subs = 0
total_subs_cefr = 0
total_target_to_avg_sub_cefr_diff = 0

target_cefr_distribution = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, None: 0}
subs_cefr_distribution = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, None: 0}

for item in swords:
    total_targets += 1
    total_target_cefr += item['target_cefr'] if item['target_cefr'] is not None else 0
    target_cefr_distribution[item['target_cefr']] += 1

    num_subs = len(item['substitutes'])
    if num_subs == 0:
        continue
    total_subs += num_subs
    subs_cefr = 0
    for sub in item['substitutes']:
        subs_cefr_distribution[sub['cefr']] += 1
        subs_cefr += sub['cefr'] if sub['cefr'] is not None else 0
    total_subs_cefr += subs_cefr
    avg_subs_cefr = subs_cefr / num_subs

    total_target_to_avg_sub_cefr_diff += avg_subs_cefr - item['target_cefr'] if item['target_cefr'] is not None else 0

print('total targets', total_targets)
print('total subs', total_subs)
print('avg subs per target', total_subs / total_targets)
print('avg target cefr', total_target_cefr / total_targets)
print('avg sub cefr', total_subs_cefr / total_subs)
print('avg cefr diff', total_target_to_avg_sub_cefr_diff / total_targets)
print('target cefr dist', target_cefr_distribution)
print('sub cefr dist', subs_cefr_distribution)