import datetime
import plotting
from flask import Flask, render_template, request

import dbconnect

app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('home.html')


@app.route('/icedexamples')
def icedexamples():
    script1,div1 = "",""
    
    return render_template('icedexamples.html', script1=script1, div1=div1)


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

    return render_template('radciexamples.html', script1=script1, div1=div1, rsl_site_list=rsl_site_list)


@app.route('/icedxradci')
def icedxradci():
    
    return render_template('icedxradci.html')


@app.route('/askiced')
def askiced():
    
    return render_template('askiced.html')


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
