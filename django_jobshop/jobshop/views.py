from django.shortcuts import render
from .algorithm.jobshop_scheduler import GAJobScheduler

# Create your views here.
def hello_view(request):
    return render(request, 'hello_django.html', {
        'data': "Hello Django ",
    })

def jobshop_view(request):
    job_data_sample = [
    {"Job_ID": "J1", "Product": "A", "Machine_Options": ["M1_1", "M1_2", "M1_3"], "Duration": 5, "Order": 1, "Optional_Workers": ["Alice", "Bob"]},
    {"Job_ID": "J2", "Product": "A", "Machine_Options": ["M2_1", "M2_2"], "Duration": 6, "Order": 2, "Optional_Workers": ["Bob", "Carol"]},
    {"Job_ID": "J3", "Product": "B", "Machine_Options": ["M1_1", "M1_2", "M1_3"], "Duration": 4, "Order": 1, "Optional_Workers": ["Alice"]},
    {"Job_ID": "J4", "Product": "B", "Machine_Options": ["M3_1", "M3_2"], "Duration": 3, "Order": 2, "Optional_Workers": ["David", "Carol"]},
    {"Job_ID": "J5", "Product": "C", "Machine_Options": ["M2_1", "M2_2"], "Duration": 7, "Order": 1, "Optional_Workers": ["Alice", "David"]},
    ]
    scheduler = GAJobScheduler(job_data_sample)
    gantt_html = scheduler.schedule_and_generate_gantt_html()
    table_html = scheduler.get_job_data_table()
    return render(request, "dist/dashboard/jobshop_table.html", {"gantt_html": gantt_html, "table_html": table_html})

def dashboard_view(request):
    return render(request, "dist/dashboard/index.html")

def download_gantt_csv(request):
    df = get_scheduling_result()  # 你自己的函式
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gantt.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def download_gantt_png(request):
    fig = get_gantt_figure()  # 你生成 plotly 圖表的函式
    scheduler = GAJobScheduler(job_data_sample)
    gantt_html = scheduler.schedule_and_generate_gantt_html()
    img_bytes = fig.to_image(format="png")
    response = HttpResponse(img_bytes, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="gantt_chart.png"'
    return response

