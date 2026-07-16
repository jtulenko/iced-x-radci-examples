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

    query = ''
    sql_select = 'SELECT '
    sql_distinct = 'DISTINCT '
    sql_from = 'FROM base_sample '
    sql_where = 'WHERE '
    sql_and = 'AND '
    sql_or = 'OR '
    sql_like = 'LIKE '
    sql_geom1 = ' ST_WITHIN( \n'
    sql_geom1 += '\tPOINT(base_sample.lon_DD, base_sample.lat_DD), \n'
    sql_geom2 = ') \n'
    join_siteONsample = 'JOIN base_site ON base_sample.site_id = base_site.id '
    join_ageONsample = 'JOIN base_calculatedage ON base_calculatedage.sample_id = base_sample.id '
    join_bealONsample = 'LEFT JOIN _be10_al26_quartz ON base_sample.id = _be10_al26_quartz.sample_id '
    join_c14ONsample = 'LEFT JOIN _c14_quartz ON base_sample.id = _c14_quartz.sample_id '
    join_he3pxolONsample = 'LEFT JOIN _he3_pxol ON base_sample.id = _he3_pxol.sample_id '
    join_he3qtzONsample = 'LEFT JOIN _he3_quartz ON base_sample.id = _he3_quartz.sample_id '
    join_ne21ONsample = 'LEFT JOIN _ne21_quartz ON base_sample.id = _ne21_quartz.sample_id '
    join_cl36ONsample = 'LEFT JOIN _cl36 ON base_sample.id = _cl36.sample_id '
    join_pubmatchONsample = 'JOIN base_samplepublicationsmatch ON base_sample.id = base_samplepublicationsmatch.sample_id '
    join_pubONpubmatch = 'JOIN base_publication ON base_publication.id = base_samplepublicationsmatch.publication_id '
    join_appsitesONsite = 'JOIN base_application_sites ON base_site.id = base_application_sites.site_id'

    att_string = ''


    if action == "inputs":
        
        application = str(request.form.get("application"))
        if application in ['None']:
            query += ''
        else:
            query += application
        
        if request.form.get("SAMPLENAME"):
            samplename = str(request.form.get("SAMPLENAME"))
            att_string += samplename
        if request.form.get("SAMPLELAT"):
            samplelat = str(request.form.get("SAMPLELAT"))
            att_string += samplelat
        if request.form.get("SAMPLELON"):
            samplelon = str(request.form.get("SAMPLELON"))
            att_string += samplelon
        if request.form.get("SAMPLEELVM"):
            sampleelvm = str(request.form.get("SAMPLEELVM"))
            att_string += sampleelvm
        if request.form.get("SAMPLETHICK"):
            samplethick = str(request.form.get("SAMPLETHICK"))
            att_string += samplethick
        if request.form.get("SAMPLEDENSITY"):
            sampledensity = str(request.form.get("SAMPLEDENSITY"))
            att_string += sampledensity
        if request.form.get("SAMPLESHIELD"):
            sampleshield = str(request.form.get("SAMPLESHIELD"))
            att_string += sampleshield
        if request.form.get("SAMPLEWHAT"):
            samplewhat = str(request.form.get("SAMPLEWHAT"))
            att_string += samplewhat
        
        if request.form.get("BECONC"):
            beconc = str(request.form.get("BECONC"))
            att_string += beconc
        if request.form.get("BECONCERR"):
            beconcerr = str(request.form.get("BECONCERR"))
            att_string += beconcerr
        if request.form.get("BEALLAB"):
            beallab = str(request.form.get("BEALLAB"))
            att_string += beallab

        query += sql_select
        query += sql_distinct
        query += att_string
        query += application
    
    return render_template('askiced.html',
                           query=query)


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
