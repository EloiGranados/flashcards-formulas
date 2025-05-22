# sm2.py

class SM2Scheduler:
    def __init__(self, ef0=2.5):
        self.ef = ef0
        self.interval = 1
        self.repetitions = 0

    def update_interval(self, sistema, nivel, quality):
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ef)
        self.ef = max(1.3, self.ef + (0.1 - (5-quality)*(0.08+(5-quality)*0.02)))
        return self.interval
