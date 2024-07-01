import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

import matplotlib.pyplot as plt
import base64
import io


def create_success_rate_chart(success_rate):
    fig, ax = plt.subplots()
    labels = 'Success', 'Failure'
    sizes = [success_rate, 100 - success_rate]
    colors = ['#4caf50', '#f44336']
    explode = (0.1, 0)  # explode the 1st slice (Success)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Success Rate')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64

def create_request_per_service_chart(service_request_counts):
    fig, ax = plt.subplots()
    service_names = [entry['name'] for entry in service_request_counts]
    request_counts = [entry['num_requests'] for entry in service_request_counts]

    ax.bar(service_names, request_counts, color='#3f51b5')
    ax.set_xlabel('Services')
    ax.set_ylabel('Number of Requests')
    ax.set_title('Requests per Service')
    ax.set_xticks(range(len(service_names)))
    ax.set_xticklabels(service_names)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64



