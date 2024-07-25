from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import tabula  # For reading PDF files

# Use Agg backend to avoid GUI issues in multi-threaded environments
plt.switch_backend('agg')

app = Flask(__name__, template_folder='/Users/rohitrajratnabansode/Downloads/feedback/Generate Charts/templates')

# Specify the directory where uploaded files will be stored
UPLOAD_FOLDER = '/Users/rohitrajratnabansode/Downloads/feedback/Generate Charts/data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            return redirect(request.url)

        # Save the uploaded file to the specified folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Redirect to the index page to display the updated list of files
        return redirect(url_for('index'))

    # Get a list of all files in the upload folder
    file_names = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]

    # Pass the list of file names to the template
    return render_template('index.html', file_names=file_names)

# Add a function to convert Excel files to CSV
def convert_excel_to_csv(file_path):
    excel_df = pd.read_excel(file_path)
    csv_path = file_path.replace('.xlsx', '.csv')
    excel_df.to_csv(csv_path, index=False)
    return csv_path

# Add a function to generate a pie chart
def generate_pie_chart(df, selected_column):
    counts = df[selected_column].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
    plt.title(f'Pie Chart - {selected_column}')
    pie_chart_path = f"pie_chart_{selected_column}.png"
    pie_chart_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pie_chart_path)
    plt.savefig(pie_chart_full_path)
    plt.close()
    return pie_chart_path

# Add a function to generate a bar chart
def generate_bar_chart(df, selected_column):
    counts = df[selected_column].value_counts()
    plt.figure(figsize=(10, 6))
    counts.plot(kind='bar')
    plt.title(f'Bar Chart - {selected_column}')
    plt.xlabel(selected_column)
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    bar_chart_path = f"bar_chart_{selected_column}.png"
    bar_chart_full_path = os.path.join(app.config['UPLOAD_FOLDER'], bar_chart_path)
    plt.savefig(bar_chart_full_path)
    plt.close()
    return bar_chart_path

@app.route('/view_chart/<chart_type>/<filename>', methods=['GET', 'POST'])
def view_chart(chart_type, filename):
    # Generate a chart from the specified file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Determine the file type
        file_ext = os.path.splitext(filename)[1].lower()

        # Convert Excel files to CSV
        if file_ext == '.xlsx':
            file_path = convert_excel_to_csv(file_path)
        elif file_ext == '.pdf':
            # You need to define a function to handle PDF conversion
            pass  # Placeholder for PDF conversion
        
        # Read the file as CSV with UTF-8 encoding
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, handle it accordingly
        error_message = "Failed to decode the file as UTF-8. The file may not be a CSV file."
        return render_template('error.html', error_message=error_message)

    chart_path = None

    if request.method == 'POST':
        # Get the selected column from the form
        selected_column = request.form.get('selected_column')

        if chart_type == 'pie':
            # Generate a pie chart
            chart_path = generate_pie_chart(df, selected_column)
        elif chart_type == 'bar':
            # Generate a bar chart
            chart_path = generate_bar_chart(df, selected_column)
        # Add more chart types as needed

    # Pass the list of available columns and chart type to the template
    columns = df.columns.tolist()
    return render_template('view_chart.html', filename=filename, columns=columns, chart_type=chart_type, chart_path=chart_path)


@app.route('/download_chart/<filename>')
def download_chart(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/clear', methods=['POST'])
def clear_files():
    # Clear all uploaded files
    file_names = os.listdir(app.config['UPLOAD_FOLDER'])
    for file_name in file_names:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        os.remove(file_path)

    # Redirect to the index page after clearing files
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
