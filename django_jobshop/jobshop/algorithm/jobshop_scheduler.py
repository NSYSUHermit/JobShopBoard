import random
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta

class GAJobScheduler:
    def __init__(self, job_data, seed=42):
        self.df_jobs = pd.DataFrame(job_data)
        self.df_jobs.sort_values(by=["Product", "Order"], inplace=True)
        self.df_jobs.reset_index(drop=True, inplace=True)
        self.seed = seed
        random.seed(self.seed)

    def generate_chromosome(self):
        task_indices = list(self.df_jobs.index)
        random.shuffle(task_indices)
        return [(i,
                 random.choice(self.df_jobs.loc[i, "Optional_Workers"]),
                 random.choice(self.df_jobs.loc[i, "Machine_Options"]))
                for i in task_indices]

    def fitness(self, chromosome):
        machine_timeline = {}
        worker_timeline = {}
        job_end_times = {}

        for idx, worker, machine in chromosome:
            job = self.df_jobs.loc[idx]
            duration = job["Duration"]
            m_time = machine_timeline.get(machine, 0)
            w_time = worker_timeline.get(worker, 0)
            prev_jobs = self.df_jobs[(self.df_jobs["Product"] == job["Product"]) & (self.df_jobs["Order"] < job["Order"])]
            pre_time = max([job_end_times.get(i, 0) for i in prev_jobs.index], default=0)
            start_time = max(m_time, w_time, pre_time)
            end_time = start_time + duration
            machine_timeline[machine] = end_time
            worker_timeline[worker] = end_time
            job_end_times[idx] = end_time

        makespan = max(job_end_times.values())
        workload_std = np.std(list(worker_timeline.values()))
        return -makespan - 0.5 * workload_std

    def run_ga(self, generations=50, population_size=30, elite_size=10, mutation_rate=0.3):
        population = [self.generate_chromosome() for _ in range(population_size)]

        for _ in range(generations):
            fitness_scores = [(ch, self.fitness(ch)) for ch in population]
            elites = sorted(fitness_scores, key=lambda x: x[1], reverse=True)[:elite_size]
            next_gen = []

            for _ in range(population_size):
                parent = random.choice(elites)[0]
                child = parent[:]
                if random.random() < mutation_rate:
                    i, j = random.sample(range(len(child)), 2)
                    child[i], child[j] = child[j], child[i]
                next_gen.append(child)

            population = next_gen

        best = max(population, key=self.fitness)
        return best

    def schedule_and_generate_gantt_html(self):
        best = self.run_ga()

        results = []
        machine_usage = {}
        worker_usage = {}
        job_end_map = {}
        start_date = datetime(2025, 6, 28, 0, 0)

        for idx, worker, machine in best:
            job = self.df_jobs.loc[idx]
            duration = job["Duration"]
            m_time = machine_usage.get(machine, 0)
            w_time = worker_usage.get(worker, 0)
            prev_jobs = self.df_jobs[(self.df_jobs["Product"] == job["Product"]) & (self.df_jobs["Order"] < job["Order"])]
            pre_time = max([job_end_map.get(j["Job_ID"], 0) for _, j in prev_jobs.iterrows()], default=0)
            start_time = max(m_time, w_time, pre_time)
            end_time = start_time + duration
            machine_usage[machine] = end_time
            worker_usage[worker] = end_time
            job_end_map[job["Job_ID"]] = end_time
            results.append({
                "Job_ID": job["Job_ID"],
                "Worker": worker,
                "Machine": machine,
                "Start_Time": start_time,
                "End_Time": end_time,
                "Start_DateTime": start_date + timedelta(hours=int(start_time)),
                "End_DateTime": start_date + timedelta(hours=int(end_time))
            })

        df_result = pd.DataFrame(results)

        fig = px.timeline(
            df_result,
            x_start="Start_DateTime",
            x_end="End_DateTime",
            y="Worker",
            color="Machine",
            text="Job_ID",
            hover_data=["Job_ID", "Machine", "Start_DateTime", "End_DateTime", "Worker"]
        )
        fig.update_layout(title="GA Job Scheduling Gantt Chart by Worker (with real time)")
        fig.update_traces(textposition='inside')
        gantt_html = pio.to_html(fig, full_html=False)
        return gantt_html
    
    def get_job_data_table(self):
        table_jobs = pd.DataFrame(self.df_jobs)
        table_jobs["Machine_Options"] = table_jobs["Machine_Options"].apply(lambda x: ", ".join(x))
        table_jobs["Optional_Workers"] = table_jobs["Optional_Workers"].apply(lambda x: ", ".join(x))

        fig = go.Figure(data=[go.Table(
            header=dict(values=list(table_jobs.columns), fill_color='lightblue', align='left'),
            cells=dict(values=[table_jobs[col] for col in table_jobs.columns], fill_color='white', align='left')
        )])
        table_html = pio.to_html(fig, full_html=False)
        return table_html
    
    def get_dataframe(self):
        table_jobs = pd.DataFrame(self.df_jobs)
        return table_jobs
    


# Run the scheduler with test data
job_data_sample = [
    {"Job_ID": "J1", "Product": "A", "Machine_Options": ["M1_1", "M1_2", "M1_3"], "Duration": 5, "Order": 1, "Optional_Workers": ["Alice", "Bob"]},
    {"Job_ID": "J2", "Product": "A", "Machine_Options": ["M2_1", "M2_2"], "Duration": 6, "Order": 2, "Optional_Workers": ["Bob", "Carol"]},
    {"Job_ID": "J3", "Product": "B", "Machine_Options": ["M1_1", "M1_2", "M1_3"], "Duration": 4, "Order": 1, "Optional_Workers": ["Alice"]},
    {"Job_ID": "J4", "Product": "B", "Machine_Options": ["M3_1", "M3_2"], "Duration": 3, "Order": 2, "Optional_Workers": ["David", "Carol"]},
    {"Job_ID": "J5", "Product": "C", "Machine_Options": ["M2_1", "M2_2"], "Duration": 7, "Order": 1, "Optional_Workers": ["Alice", "David"]},
]

scheduler = GAJobScheduler(job_data_sample)
gantt_html_output = scheduler.schedule_and_generate_gantt_html()
gantt_html_output[:500]  # Show a preview of the generated HTML
