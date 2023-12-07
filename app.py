from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

plt.switch_backend('agg')

app = Flask(__name__, template_folder='/path/to/your/templates/folder')


UPLOAD_FOLDER = '/path/to/your/data/folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        
        if file.filename == '':
            return redirect(request.url)

        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        
        return redirect(url_for('index'))

    
    file_names = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]

    
    return render_template('index.html', file_names=file_names)

@app.route('/download_pie_chart/<filename>')
def download_pie_chart(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/clear', methods=['POST'])
def clear_files():
    
    file_names = os.listdir(app.config['UPLOAD_FOLDER'])
    for file_name in file_names:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        os.remove(file_path)

    
    return redirect(url_for('index'))

@app.route('/view_pie_chart/<filename>', methods=['GET', 'POST'])
def view_pie_chart(filename):
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        
        error_message = "Failed to decode the file as UTF-8. The file may not be a CSV file."
        return render_template('error.html', error_message=error_message)

    pie_chart_path = None  

    if request.method == 'POST':
        
        selected_column = request.form.get('selected_column')

        if selected_column in df.columns:
            
            counts = df[selected_column].value_counts()
            categories = counts.index.tolist()

            
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            plt.title(f'Distribution of {selected_column}')

            
            pie_chart_path = f"pie_chart_{selected_column}.png"
            pie_chart_full_path = os.path.join(app.config['UPLOAD_FOLDER'], pie_chart_path)
            plt.savefig(pie_chart_full_path)
            plt.close()  
    
    
    columns = df.columns.tolist()
    return render_template('view_pie_chart.html', filename=filename, columns=columns, pie_chart_path=pie_chart_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
