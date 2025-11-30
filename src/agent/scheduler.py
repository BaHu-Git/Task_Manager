import datetime

class Scheduler:
    def __init__(self, start_date=None):
        self.start_date = start_date or datetime.datetime.utcnow()

    def schedule(self, tasks):
        # tasks: [{"description": "...", "depends_on": null or int, "duration": 30}, ...]
        timeline = []
        current_time = self.start_date

        for task in tasks:
            timeline.append({
                "description": task["description"],
                "start": current_time,
                "duration": task["duration"]
            })
            current_time += datetime.timedelta(minutes=task["duration"])

        return timeline
