import datetime
import plotting
from flask import Flask, render_template, request
from tabulate import tabulate

import dbconnect

app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('home.html')


@app.route('/icedexamples')
def icedexamples():
    script1, div1 = plotting.c14_psat()
    script2, div2 = plotting.gris_tdd()
    script3, div3 = plotting.created_at()
    script4, div4 = plotting.ratio_elv_plot()

    return render_template('icedexamples.html',
                           script1=script1, div1=div1,
                           script2=script2, div2=div2,
                           script3=script3, div3=div3,
                           script4=script4, div4=div4)


@app.route('/radciexamples', methods=["GET", "POST"])
def radciexamples():

    rsl_site_query = f"""SELECT DISTINCT base_rsl_site.name
            FROM base_rsl_site"""
    
    query_result = dbconnect.querier_radci(rsl_site_query)

    rsl_site_list = query_result[1:,0].astype(str).tolist()

    script1,div1 = "", ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "rsl_plot":
            rsl_site = str(request.form.get("rsl_site"))

            script1, div1 = plotting.rsl_plot(rsl_site)

    return render_template('radciexamples.html',
                           script1=script1, div1=div1,
                           rsl_site_list=rsl_site_list)


@app.route('/icedxradci')
def icedxradci():
    
    return render_template('icedxradci.html')


@app.route('/askiced', methods=["GET", "POST"])
def askiced():

    action = request.form.get("action")

    if action == "application":
        application = str(request.form.get("application"))

        print_result = print(application)
    
    return render_template('askiced.html',
                           print_result = print_result)


@app.route('/icedlab')
def icedlab():
    
    return render_template('icedlab.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)
