# tracker.py

import json, datetime

class MetricsTracker:
    def __init__(self, path="metricas.json"):
        self.path = path
        try:
            with open(path,"r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []

    def log_attempt(self, sistema, nivel, quality, time_spent):
        registro = {
            "sistema": sistema,
            "nivel": nivel,
            "quality": quality,
            "time_spent": time_spent,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.data.append(registro)
        with open(self.path,"w") as f:
            json.dump(self.data, f, indent=2)

    def get_stats(self):
        from collections import defaultdict
        stats = defaultdict(lambda: defaultdict(list))
        for r in self.data:
            stats[r["sistema"]][r["nivel"]].append(r["quality"])
        return {
            s: {n: sum(v)/len(v) for n,v in niveles.items()}
            for s,niveles in stats.items()
        }

    def get_dataframe(self):
        import pandas as pd
        return pd.DataFrame(self.data)
