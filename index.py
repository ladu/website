from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import pandas as pd
from pulp import *
import shutil

app = Flask(__name__)



# Define the upload folder path as an environment variable
UPLOAD_FOLDER = 'uploads'

# Delete and create the UPLOAD_FOLDER at every reload
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/')
# def index():
#     return render_template('index.html')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        filename = 'uploaded_file.xlsx'
        if 'file' in request.files:
            file = request.files['file']

            if not file:
                return render_template('index.html', error='No file selected!')
            if file and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                df = df.iloc[0:6,0:6]
                data = df.to_dict(orient='records')
                columns = [{"title": str(col)} for col in df.columns]
                return render_template('index.html', data=data, columns=columns)
            
        elif request.form['action'] == 'Solve':
                df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                df_2 = do_TSP(df)
                return render_template('display.html', tables=[df_2.to_html(classes='data')], titles=['Optimal Tour'])
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['inputFile']
#     df = pd.read_excel(file)
#     df1, df2 = do_TSP(df)
#     df1 = df1.iloc[0:6,0:6]
#     return render_template('display.html', tables=[df1.to_html(classes='data'), df2.to_html(classes='data')], titles=['Sample of Input data', 'Optimal Tour'])

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file(filename):
    # return a secure version of the filename
    return secure_filename(filename)



def do_TSP(df):
    # Define problem and decision variables
    prob = LpProblem("TSP Problem", LpMinimize)

    # Define the number of locations
    n_locations = len(df.columns) - 1
    distance_matrix = {}
    for i in range(n_locations):
        for j in range(n_locations):
            distance_matrix[i,j] = df.loc[i,f"Location {j+1}"]

    # Define the decision variables for the TSP problem
    x = {}
    for i in range(n_locations):
        for j in range(n_locations):
            x[(i,j)] = LpVariable("x_{}_{}".format(i, j), cat='Binary')

    # Define the objective function
    prob += lpSum([distance_matrix[i,j]*x[(i,j)] for i in range(n_locations) for j in range(n_locations)])

    # Define the constraints
    for i in range(n_locations):
        prob += x[(i,i)] == 0
    for i in range(n_locations):
        prob += lpSum([x[(i,j)] for j in range(n_locations)]) == 1
    for j in range(n_locations):
        prob += lpSum([x[(i,j)] for i in range(n_locations)]) == 1

    # Define the subtour elimination constraints
    u = LpVariable.dicts("u", [i for i in range(n_locations)], lowBound=0, upBound=n_locations-1, cat='Integer')
    for i in range(1,n_locations):
        for j in range(1,n_locations):
            if i != j:
                prob += u[i] - u[j] + n_locations*x[(i,j)] <= n_locations - 1

    # Solve the problem
    prob.solve()

    # Print the optimal solution
    # print("Total distance travelled: ", value(prob.objective))

    # Print the optimal tour
    opt_tour_df = pd.DataFrame()
    tour = [0]
    i = 0
    data = {"Optimal tour":f"Location {i+1}"}
    opt_tour_df = pd.concat([opt_tour_df, pd.DataFrame(data, index = [0])], ignore_index=True, axis = 0)
    while len(tour) < n_locations:
        for j in range(n_locations):
            if x[(i,j)].varValue == 1:
                tour.append(j)
                i = j
                data = {"Optimal tour":f"Location {i+1}"}
                opt_tour_df = pd.concat([opt_tour_df, pd.DataFrame(data, index = [0])], ignore_index=True, axis = 0)
                break
    # print("Optimal tour: ", tour)

    return opt_tour_df



if __name__ == '__main__':
    app.run(port=8000, debug=True)
