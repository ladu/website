from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['inputFile']
    df = pd.read_excel(file)
    # df = do_manipulation(df)
    return render_template('display.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

def do_manipulation(df):
    col_names = df.columns
    df.rename({col_names[0]: 'Name', col_names[1]: 'Age', col_names[2]: "Weight"}, axis=1, inplace=True)
    return df

if __name__ == '__main__':
    app.run(debug=True)
