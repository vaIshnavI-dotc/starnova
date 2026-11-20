import json

def source_stats_row(row):
    d = dict(row)
    for key in ('sebi_registered',):
        if d.get(key) is not None: d[key] = bool(d[key])
    d.setdefault('raw_hit_rate', None)
    d.setdefault('shrunk_hit_rate', d.get('post_mean'))
    d.setdefault('overconfidence_gap', None)
    return d
