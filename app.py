from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Use Agg backend to avoid GUI issues in multi-threaded environments
plt.switch_backend('agg')

app = Flask(__name__, template_folder='/Users/rohitrajratnabansode/Downloads/feedback/templates')

# Specify the directory where uploaded files will be stored
UPLOAD_FOLDER = '/Users/rohitrajratnabansode/Downloads/feedback/data'
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

@app.route('/download_pie_chart/<filename>')
def download_pie_chart(filename):
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

@app.route('/view_pie_chart/<filename>', methods=['GET', 'POST'])
def view_pie_chart(filename):
    # Generate a pie chart from the specified CSV file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Attempt to read the file as CSV with UTF-8 encoding
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, handle it accordingly
        error_message = "Failed to decode the file as UTF-8. The file may not be a CSV file."
        return render_template('error.html', error_message=error_message)

    pie_chart_path = None  # Initialize pie_chart_path here

    if request.method == 'POST':
        # Get the selected column from the form
        selected_column = request.form.get('selected_column')

        if selected_column in df.columns:
            # Generate the pie chart using the selected column
            counts = df[selected_column].value_counts()
            categories = counts.index.tolist()

            # Create a pie chart
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            plt.title(f'Distribution of {selected_column}')

            # Save the pie chart to a file
            pie_chart_path = f"pie_chart_{selected_column}.png"
            pie_chart_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pie_chart_path)
            plt.savefig(pie_chart_full_path)
            plt.close()  # Close the plot to release memory
    
    # Pass the list of available columns to the template
    columns = df.columns.tolist()
    return render_template('view_pie_chart.html', filename=filename, columns=columns, pie_chart_path=pie_chart_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
