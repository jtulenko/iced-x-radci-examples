import datetime
import plotting
from flask import Flask, render_template, request

import dbconnect

app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/radciexamples', methods=["GET", "POST"])
def radciexamples():

    rsl_site_query = f"""SELECT DISTINCT base_rsl_site.name
            FROM base_rsl_site"""
    
    query_result = dbconnect.querier_radci(rsl_site_query)

    rsl_site_list = query_result[1:,0].astype(str)

    script1,div1 = "", ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "rsl_plot":
            rsl_site = str(request.form.get("rsl_site"))

            script1, div1 = plotting.rsl_plot(rsl_site)

    return render_template('radciexamples.html', script1=script1, div1=div1, rsl_site_list=rsl_site_list)

@app.route('/sealevel', methods=["GET", "POST"])
def sealevel():
    script1,div1 = "",""
    script2,div2 = "",""
    if request.method == "POST":
        action = request.form.get("action")

        if action == "map_plot":
            rsl_recon = str(request.form.get("rsl_recon"))
            lat_min = int(request.form.get("lat_min", -90))
            lat_max = int(request.form.get("lat_max", 90))
            lon_min = int(request.form.get("lon_min", -180))
            lon_max = int(request.form.get("lon_max", 180))
            age_value = int(request.form.get("age_slider", 0))
            rsl_max = int(request.form.get("rsl_max", 100))
            rsl_min = int(request.form.get("rsl_min", -100))

            script1, div1 = plotting.sealevel_plot1(lat_min, lat_max, lon_min, lon_max, age_value, rsl_recon, rsl_min, rsl_max)

        elif action == "ts_plot":
            ts_recon = str(request.form.get("rsl_reconTS"))
            lat_index = int(request.form.get("lat_ts", 63))
            lon_index = int(request.form.get("lon_ts", 19))
            age_min = int(request.form.get("age_min", 0))
            age_max = int(request.form.get("age_max", 400))

            script2, div2 = plotting.sealevel_ts(lat_index, lon_index, age_min, age_max, ts_recon)


    return render_template('sealevel.html', script1=script1, div1=div1, script2=script2, div2=div2)

@app.route('/deformation')
def deformation():
    
    return render_template('deformation.html')

@app.route('/velocity', methods=["GET", "POST"])
def velocity():
    script1,div1 = "",""
    if request.method == "POST":
        action = request.form.get("action")

        if action == "map_plot":
            vdef_recon = str(request.form.get("vdef_recon"))
            lat_min = int(request.form.get("lat_min", -90))
            lat_max = int(request.form.get("lat_max", 90))
            lon_min = int(request.form.get("lon_min", -180))
            lon_max = int(request.form.get("lon_max", 180))
            vdef_max = int(request.form.get("vdef_max", 10))
            vdef_min = int(request.form.get("vdef_min", -10))

            script1, div1 = plotting.vvel_plot1(lat_min, lat_max, lon_min, lon_max, vdef_recon, vdef_min, vdef_max)

    
    return render_template('velocity.html', script1=script1, div1=div1)

@app.route('/gravity')
def gravity():
    
    return render_template('gravity.html')

@app.route('/stress')
def stress():
    
    return render_template('stress.html')

@app.route('/rotation')
def rotation():
    
    return render_template('rotation.html')

@app.route('/topography')
def topography():
    
    return render_template('topography.html')

@app.route('/feedback')
def feedback():
    
    return render_template('feedback.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=5000, debug=True)
