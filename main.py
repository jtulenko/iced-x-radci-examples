import datetime
import plotting
from flask import Flask, render_template, request, abort
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
    query_statement = 'SQL RESULT:'


    if action == "inputs":
        
        #sample attributes
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

        #age attributes
        if request.form.get("AGEST"):
            agest = str(request.form.get("AGEST"))
            att_string += agest
        if request.form.get("ERRST"):
            errst = str(request.form.get("ERRST"))
            att_string += errst
        if request.form.get("AGELM"):
            agelm = str(request.form.get("AGELM"))
            att_string += agelm
        if request.form.get("ERRLM"):
            errlm = str(request.form.get("ERRLM"))
            att_string += errlm
        if request.form.get("AGELSDN"):
            agelsdn = str(request.form.get("AGELSDN"))
            att_string += agelsdn
        if request.form.get("ERRLSDN"):
            errlsdn = str(request.form.get("ERRLSDN"))
            att_string += errlsdn
        if request.form.get("NUCLIDE"):
            nuclide = str(request.form.get("NUCLIDE"))
            att_string += nuclide

        #site attributes
        if request.form.get("SITESHRTNM"):
            siteshrtnm = str(request.form.get("SITESHRTNM"))
            att_string += siteshrtnm
        if request.form.get("SITELGNM"):
            sitelgnm = str(request.form.get("SITELGNM"))
            att_string += sitelgnm
        if request.form.get("SITEWHAT"):
            sitewhat = str(request.form.get("SITEWHAT"))
            att_string += sitewhat
        
        #be-10 attributes
        if request.form.get("BECONC"):
            beconc = str(request.form.get("BECONC"))
            att_string += beconc
        if request.form.get("BECONCERR"):
            beconcerr = str(request.form.get("BECONCERR"))
            att_string += beconcerr
        if request.form.get("BEALLAB"):
            beallab = str(request.form.get("BEALLAB"))
            att_string += beallab

        #al-26 attributes
        if request.form.get("ALCONC"):
            alconc = str(request.form.get("ALCONC"))
            att_string += alconc
        if request.form.get("ALCONCERR"):
            alconcerr = str(request.form.get("ALCONCERR"))
            att_string += alconcerr

        #c-14 attributes
        if request.form.get("CCONC"):
            cconc = str(request.form.get("CCONC"))
            att_string += cconc
        if request.form.get("CCONCERR"):
            cconcerr = str(request.form.get("CCONCERR"))
            att_string += cconcerr
        if request.form.get("CLAB"):
            clab = str(request.form.get("CLAB"))
            att_string += clab

        #He-3 pxol attributes
        if request.form.get("HEPXOLCONC"):
            hepxolconc = str(request.form.get("HEPXOLCONC"))
            att_string += hepxolconc
        if request.form.get("HEPXOLCONCERR"):
            hepxolconcerr = str(request.form.get("HEPXOLCONCERR"))
            att_string += hepxolconcerr
        if request.form.get("HEPXOLLAB"):
            hepxollab = str(request.form.get("HEPXOLLAB"))
            att_string += hepxollab

        #He-3 in qtz attributes
        if request.form.get("HEQTZCONC"):
            heqtzconc = str(request.form.get("HEQTZCONC"))
            att_string += heqtzconc
        if request.form.get("HEQTZCONCERR"):
            heqtzconcerr = str(request.form.get("HEQTZCONCERR"))
            att_string += heqtzconcerr
        if request.form.get("HEQTZLAB"):
            heqtzlab = str(request.form.get("HEQTZLAB"))
            att_string += heqtzlab

        #Ne-21 in qtz attributes
        if request.form.get("NEQTZCONC"):
            neqtzconc = str(request.form.get("NEQTZCONC"))
            att_string += neqtzconc
        if request.form.get("NEQTZCONCERR"):
            neqtzconcerr = str(request.form.get("NEQTZCONCERR"))
            att_string += neqtzconcerr
        if request.form.get("NEQTZLAB"):
            neqtzlab = str(request.form.get("NEQTZLAB"))
            att_string += neqtzlab

        #Cl-36 attributes
        if request.form.get("CLCONC"):
            clconc = str(request.form.get("CLCONC"))
            att_string += clconc
        if request.form.get("CLCONCERR"):
            clconcerr = str(request.form.get("CLCONCERR"))
            att_string += clconcerr
        if request.form.get("CLLAB"):
            cllab = str(request.form.get("CLLAB"))
            att_string += cllab

        #publication attributes
        if request.form.get("PUBDOI"):
            pubdoi = str(request.form.get("PUBDOI"))
            att_string += pubdoi
        if request.form.get("PUBCITE"):
            pubcite = str(request.form.get("PUBCITE"))
            att_string += pubcite
            #need to work on this to set up query syntax to concat citation like we do on ICE-D pages

        query += sql_select
        query += sql_distinct
        query += att_string
        query += 'base_sample.id'
        query += '\n'
        query += sql_from
        query += '\n'

        if any(request.form.get(name) for name in ["AGEST", "ERRST", "AGELM", "ERRLM", "AGELSDN", "ERRLSDN", "NUCLIDE"]):
            query += join_ageONsample
            query += '\n'

        if any(request.form.get(name) for name in ["PUBDOI", "PUBCITE"]):
            query += join_pubmatchONsample
            query += '\n'
            query += join_pubONpubmatch
            query += '\n'


        if request.form["maxlat"]:
            try:
                maxlat = float(request.form["maxlat"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_sample.lat_DD <= {maxlat}"
            query += '\n'

        if request.form["minlat"]:
            try:
                minlat = float(request.form["minlat"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_sample.lat_DD >= {minlat}"
            query += '\n'

        if request.form["maxlon"]:
            try:
                maxlon = float(request.form["maxlon"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_sample.lon_DD <= {maxlon}"
            query += '\n'

        if request.form["minlon"]:
            try:
                minlon = float(request.form["minlon"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_sample.lon_DD >= {minlon}"
            query += '\n'

        if request.files.get("uploadoutline"):
            file = request.files.get("uploadoutline")
            filename = file.filename.lower()
            if not (filename.endswith(".geojson") or filename.endswith(".kml")):
                abort(400)
        #this might turn into a pain so I am going to just figure this out later
                
        site_type = str(request.form.get("site_type"))
        if site_type in ['None']:
            query += ''
        else:
            query += sql_and
            query += site_type
            query += '\n'
        
        sample_type = str(request.form.get("sample_type"))
        if sample_type in ['None']:
            query += ''
        else:
            query += sql_and
            query += sample_type
            query += '\n'

        if request.form["maxage"]:
            try:
                maxage = float(request.form["maxage"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_calculatedage.t_St <= {maxage}"
            query += '\n'
        
        if request.form["minage"]:
            try:
                minage = float(request.form["minage"])
            except ValueError:
                abort(400)
            query += sql_and
            query += f"base_calculatedage.t_St >= {minage}"
            query += '\n'

        application = str(request.form.get("application"))
        if application in ['None']:
            query += ''
        else:
            query += sql_and
            query += application
            query += '\n'
    
    return render_template('askiced.html',
                           query=query,
                           query_statement=query_statement)


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
