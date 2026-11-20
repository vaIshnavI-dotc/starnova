import json

def source_stats_row(row):
    d = dict(row)
    for key in ('sebi_registered',):
        if d.get(key) is not None:
            d[key] = bool(d[key])
    d.setdefault('raw_hit_rate', None)
    d.setdefault('shrunk_hit_rate', d.get('post_mean'))
    d.setdefault('overconfidence_gap', None)

    # Contract required fields aliases
    d['id'] = d.get('source_id')
    d['name'] = d.get('display_name')
    d['type'] = d.get('source_type')
    d['tips_total'] = d.get('n_tips', 0) or 0
    d['tips_worked'] = d.get('n_hits', 0) or 0

    ev = d.get('evidence_level') or 'none'
    if ev in ('none', 'low', 'insufficient'):
        d['label'] = 'Too early to tell'
    elif not d.get('label'):
        shrunk = d.get('shrunk_hit_rate') or 0.0
        d['label'] = 'Consistent alpha' if shrunk >= 0.6 else ('Hit or miss' if shrunk >= 0.45 else 'Unreliable')

    return d
