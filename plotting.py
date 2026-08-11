from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import Span, HoverTool, ColorBar, LinearColorMapper, GeoJSONDataSource
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.palettes import Viridis256
import pandas
import numpy 
from numpy import array, log, tan, pi
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import xarray as xr
import netCDF4 as nc
import geopandas as gpd
import json
from cmcrameri import cm
import gc
from tabulate import tabulate
from pyproj import Transformer
import json

import dbconnect

def rsl_plot(rsl_plot):
    rsl_plot = rsl_plot

    rsl_plot_query = f"""SELECT base_sample.name, base_calibratedage.age_calyrBP, base_calibratedage.minage_1sd_calyrBP, base_calibratedage.maxage_1sd_calyrBP, base_rsl_info.sealevel_index_elev_m, base_rsl_info.sealevel_index_elev_m_err
        FROM base_sample
        LEFT JOIN base_calibratedage ON base_sample.id = base_calibratedage.sample_id
        LEFT JOIN base_rsl_info ON base_sample.id = base_rsl_info.sample_id
        LEFT JOIN base_rsl_site ON base_rsl_site.id = base_rsl_info.rsl_site_id
        WHERE base_rsl_site.name LIKE "%{rsl_plot}%"
        AND base_calibratedage.reservoir_corr_id = 1"""
    
    site_result = dbconnect.querier_radci(rsl_plot_query)

    sample = site_result[1:,0]
    calage = site_result[1:,1].astype(float)
    calmin = site_result[1:,2].astype(float)
    calmax = site_result[1:,3].astype(float)
    elev = site_result[1:,4].astype(float)
    elev_err = (site_result[1:,5].astype(float)) * 100
    elev_min = elev - elev_err
    elev_max = elev + elev_err

    data = {
        'x': array(calage),
        'xmin': array(calmin),
        'xmax': array(calmax),
        'y': array(elev),
        'ymin': array(elev_min),
        'ymax': array(elev_max),
        'sample': array(sample)
    }

    p = figure(title=f"{rsl_plot} RSL Site", width=855, height=540, x_axis_label="Cal yr BP", y_axis_label="Elevation (m)", tools="pan,wheel_zoom,save,reset", x_range=((min(calmin) * 0.9), (max(calmax)*1.1)), y_range=((min(elev_min) * 0.9), (max(elev_max)*1.1)))
    p.rect(x=(calmax + calmin)/2, y=(elev_min + elev_max)/2, width=calmax - calmin, height=elev_max - elev_min, fill_alpha=0.75, fill_color='#d3d3d3')
    p.segment(x0=calage, y0=elev_min, x1=calage, y1=elev_max, line_width=3, line_color='#014421')
    p.segment(x0=calmin, y0=elev, x1=calmax, y1=elev, line_width=3, line_color='#014421')
    p.segment(x0=calmin, y0=elev_min, x1=calmax, y1=elev_min, line_width=1, line_color='#d3d3d3')
    p.segment(x0=calmin, y0=elev_max, x1=calmax, y1=elev_max, line_width=1, line_color='#d3d3d3')
    p.segment(x0=calmin, y0=elev_min, x1=calmin, y1=elev_max, line_width=1, line_color='#d3d3d3')
    p.segment(x0=calmax, y0=elev_min, x1=calmax, y1=elev_max, line_width=1, line_color='#d3d3d3')
    scatter = p.scatter(x='x', y='y', size=20, source=data, fill_alpha=0, line_alpha=0)
    p.add_tools(HoverTool(renderers=[scatter],tooltips=[("Sample name", "@sample")]))


    plot_script, plot_div = components(p)

    return components(p)

def core_plot(core_data):
    core_data = core_data

    core_query = f"""SELECT DISTINCT base_core.name, base_sample.name, base_calibratedage.age_calyrBP, base_calibratedage.minage_1sd_calyrBP, base_calibratedage.maxage_1sd_calyrBP, base_sample.sample_top_depth_m, base_sample.sample_bottom_depth_m
            FROM base_core
            JOIN base_sample ON base_sample.core_id = base_core.id
            JOIN base_calibratedage ON base_sample.id = base_calibratedage.sample_id
            WHERE base_core.name LIKE "%{core_data}%"
            AND base_calibratedage.reservoir_corr_id = 1"""
    
    core_result = dbconnect.querier_radci(core_query)

    core = core_result[1:,0]
    sample = core_result[1:,1]
    age = core_result[1:,2].astype(float)
    agemin = core_result[1:,3].astype(float)
    agemax = core_result[1:,4].astype(float)
    depthmin = core_result[1:,5].astype(float)
    depthmax = core_result[1:,6].astype(float)

    data = {
        'x': array(age),
        'xmin': array(agemin),
        'xmax': array(agemax),
        'ymin': array(depthmin),
        'ymax': array(depthmax),
        'sample': array(sample),
        'core': array(core)
    }

    p = figure(title=f"{core_data} Core", width=855, height=540, x_axis_label="Cal yr BP", y_axis_label="Core Depth (m)", tools="pan,wheel_zoom,save,reset", x_range=((min(agemin) * 0.9), (max(agemax)*1.1)), y_range=((max(depthmax)*1.1), 0))
    p.rect(x=(agemax + agemin)/2, y=(depthmin + depthmax)/2, width=agemax - agemin, height=depthmax - depthmin, fill_alpha=0.75, fill_color='#d3d3d3')
    p.segment(x0=age, y0=depthmin, x1=age, y1=depthmax, line_width=3, line_color='#014421')
    p.segment(x0=agemin, y0=(depthmin + depthmax)/2, x1=agemax, y1=(depthmin + depthmax)/2, line_width=3, line_color='#014421')
    p.segment(x0=agemin, y0=depthmin, x1=agemax, y1=depthmin, line_width=1, line_color='#d3d3d3')
    p.segment(x0=agemin, y0=depthmax, x1=agemax, y1=depthmax, line_width=1, line_color='#d3d3d3')
    p.segment(x0=agemin, y0=depthmin, x1=agemin, y1=depthmax, line_width=1, line_color='#d3d3d3')
    p.segment(x0=agemax, y0=depthmin, x1=agemax, y1=depthmax, line_width=1, line_color='#d3d3d3')
    scatter = p.scatter(x='x', y='ymin', size=20, source=data, fill_alpha=0, line_alpha=0)
    p.add_tools(HoverTool(renderers=[scatter],tooltips=[("Sample name", "@sample")]))

    plot_script, plot_div = components(p)

    return components(p)

def c14_psat():

    c14_psat_query = f"""SELECT DISTINCT _c14_quartz.N14_atoms_g, base_sample.elv_m, base_calculatedage.t_St, base_sample.name
	    FROM _c14_quartz
	    JOIN base_sample ON _c14_quartz.sample_id = base_sample.id
	    JOIN base_site ON base_sample.site_id = base_site.id
	    JOIN base_calculatedage ON base_calculatedage.sample_id = base_sample.id
	    JOIN base_application_sites ON base_site.id = base_application_sites.site_id
	    WHERE base_calculatedage.t_St != 0
	    AND base_sample.elv_m > 1
	    AND _c14_quartz.N14_atoms_g / base_calculatedage.t_St < 100
	    AND base_calculatedage.t_St < 25000
	    AND base_calculatedage.nuclide LIKE "%N14quartz%"
        AND base_sample.name NOT LIKE "%10-MPS-046-NNS%"
	    AND base_sample.name NOT LIKE "%10-MPS-008-NNS%"
	    AND base_sample.name NOT LIKE "%10-MPS-006-COU%"
	    AND base_application_sites.application_id = 1"""
    
    list_result = dbconnect.querier_iced(c14_psat_query)

    x1 = (list_result[1:,0].astype(float)) * 0.00012096809
    y1 = list_result[1:,1].astype(float)
    sizes = (list_result[1:,2].astype(float)) ** (1/3)
    name = list_result[1:,3]

    data = {'x1': array(x1),
            'y1': array(y1),
            'sizes': array(sizes),
            'name': array(name)}

    p= figure(width=750, height=500, x_axis_type="log", title="Saturation concentration of in-situ C-14")
    p.xaxis.axis_label = "N * I"
    p.yaxis.axis_label = "Elevation (m)"

    p.scatter('x1','y1', size='sizes', source=data, fill_color='rgba(255, 168, 38, 1)', fill_alpha=0.7, line_color='grey', line_alpha=0.5, marker="circle")
    p.add_tools(HoverTool(tooltips=[("Sample name", "@name"),("Age (ka)", "@sizes"),("N * I", "@x1")]))


    plot_script, plot_div = components(p)

    return components(p)

def gris_tdd():

    gris_tdd_query = f"""SELECT base_sample.lon_DD, base_calculatedage.t_St, base_calculatedage.dtint_St, base_sample.name
        FROM base_sample
        JOIN base_site ON base_sample.site_id = base_site.id
        JOIN base_application_sites ON base_site.id = base_application_sites.site_id
        JOIN base_calculatedage ON base_sample.id = base_calculatedage.sample_id
        WHERE base_application_sites.application_id = 3
        AND base_sample.what LIKE "%oulder%"
        AND (base_sample.lat_DD >= 64.8 AND base_sample.lat_DD <=71)
        AND (base_sample.lon_DD >= -60 AND base_sample.lon_DD <= -48)
        AND base_calculatedage.t_St != 0
        AND base_calculatedage.t_St IS NOT NULL;"""
    
    list_result = dbconnect.querier_iced(gris_tdd_query)

    x1 = list_result[1:,0].astype(float)
    y1 = ((list_result[1:,1].astype(float)) / 1.0134) / 1000
    y_min = y1 - (((list_result[1:,2].astype(float)) / 1.0134) / 1000)
    y_max = y1 + (((list_result[1:,2].astype(float)) / 1.0134) / 1000)
    name = list_result[1:,3].astype(str)

    data = {'x1': array(x1),
            'y1': array(y1),
            'y_min': array(y_min),
            'y_max': array(y_max),
            'name': array(name)}

    p= figure(width=750, height=500, y_range=(16,5), title="Western Greenland longitude versus boulder ages")
    p.xaxis.axis_label = "Longitude (decimal degrees)"
    p.yaxis.axis_label = "Exposure ages using aproximated Arctic PR and St Scaling (ka)"

    events = [9.3, 8.2]

    e1 = Span(location=events[0], dimension='width', line_color='grey', line_alpha=0.5, line_width=20)
    e1.level = 'underlay'

    e2 = Span(location=events[1], dimension='width', line_color='grey', line_alpha=0.5, line_width=20)
    e2.level = 'underlay'

    p.add_layout(e1)
    p.add_layout(e2)
    p.line([],[], line_color='grey', line_alpha=0.5, line_width=20, legend_label= "grey bars = 9.3 and 8.2 ka events")
    p.legend.location = "top_left"

    p.vbar(x='x1', bottom='y_min', top='y_max', source=data, width=.0005, line_color='black')
    p.scatter('x1','y1', source=data, size = 12, fill_color='rgba(0, 128, 128, 1)', fill_alpha=0.9, line_color='grey', line_alpha=0.5, marker="circle")
    p.add_tools(HoverTool(tooltips=[("Sample name", "@name"),("Age (ka)", "@y1")]))

    plot_script, plot_div = components(p)

    return components(p)

def created_at():
    
    created_at_query=f"""SELECT LEFT(base_sample.created_at,4), SUBSTRING(base_sample.created_at,6,2), SUBSTRING(base_sample.created_at,9,2)
        FROM base_sample
        WHERE base_sample.id > 21901"""
    
    list_result = dbconnect.querier_iced(created_at_query)

    date1 = list_result[1:,0].astype(float)
    date2 = (list_result[1:,1].astype(float)) / 12
    date3 = (list_result[1:,2].astype(float)) / 365

    date = date1 + date2 + date3

    p= figure(width=750, height=500, title="Dates for samples entered into ICE-D")
    p.xaxis.axis_label = "Date Entered (decimal date)"
    p.yaxis.axis_label = "Sample Count"

    bins = numpy.arange(numpy.min(date),numpy.max(date) + (5/365), (5/365))
    hist, edges = numpy.histogram(date, bins=bins)

    p.quad(top=hist,bottom=0,left=edges[:-1], right=edges[1:], fill_color="navy", line_color="white", alpha=0.5)

    plot_script, plot_div = components(p)
    
    return components(p)

def ratio_elv_plot():

    ratio_elev_query=f"""SELECT DISTINCT _be10_al26_quartz.N10_atoms_g, _be10_al26_quartz.N26_atoms_g, base_sample.elv_m, _be10_al26_quartz.delN10_atoms_g, _be10_al26_quartz.delN26_atoms_g, base_sample.name
        FROM base_sample
        JOIN _be10_al26_quartz ON base_sample.id = _be10_al26_quartz.sample_id
        JOIN base_calculatedage ON base_calculatedage.sample_id = base_sample.id
        JOIN base_site ON base_site.id = base_sample.site_id
        JOIN base_application_sites ON base_application_sites.site_id = base_site.id
        WHERE base_sample.elv_m IS NOT NULL
        AND base_sample.elv_m != 0
        AND _be10_al26_quartz.N10_atoms_g IS NOT NULL
        AND _be10_al26_quartz.N10_atoms_g != 0
        AND _be10_al26_quartz.N26_atoms_g IS NOT NULL
        AND _be10_al26_quartz.N26_atoms_g != 0
        AND base_sample.what LIKE "%oulder%"
        AND base_calculatedage.t_St > 25000
        AND base_application_sites.application_id = 2"""
    
    list_result = dbconnect.querier_iced(ratio_elev_query)

    x1= list_result[1:,2].astype(float)
    y1= (list_result[1:,1].astype(float)) / (list_result[1:,0].astype(float))
    y_min = y1 - (((list_result[1:,3].astype(float)) / (list_result[1:,0].astype(float)))**2) + (((list_result[1:,4].astype(float)) / (list_result[1:,1].astype(float)))**0.5)
    y_max = y1 + (((list_result[1:,3].astype(float)) / (list_result[1:,0].astype(float)))**2) + (((list_result[1:,4].astype(float)) / (list_result[1:,1].astype(float)))**0.5)
    sizes = (list_result[1:,0].astype(float)) ** (1/5)
    name = list_result[1:,5].astype(str)

    data = {'x1': array(x1),
            'y1': array(y1),
            'y_min': array(y_min),
            'y_max': array(y_max),
            'sizes': array(sizes),
            'name': array(name)}


    par = numpy.polyfit(x1, y1, 1, full=True)
    slope=par[0][0]
    intercept=par[0][1]
    y_predicted = [slope*i + intercept  for i in x1]
    correlation_matrix = numpy.corrcoef(x1, y1)
    correlation_xy = correlation_matrix[0,1]
    r_squared = correlation_xy**2

    p= figure(width=750, height=500, title="[Al]/[Be] ratio with Elevation", y_range=(4,10))
    p.xaxis.axis_label = "Elevation (m)"
    p.yaxis.axis_label = "[Al]/[Be]"

    p.vbar(x='x1', bottom='y_min', top='y_max', width=1, source=data, line_color='black')
    p.scatter('x1', 'y1', size='sizes', source=data, fill_color= 'rgba(48, 92, 222, 1)', fill_alpha=0.9, line_color='grey', line_width=0.5, legend_label = 'size = [10Be] ^ (1/5)', marker="circle")
    p.line(x1,y_predicted, color='black',legend_label='y= '+str(round(slope,6))+'x+'+str(round(intercept,2))+'   r^2 ='+str(round(r_squared,6)))
    p.add_tools(HoverTool(tooltips=[("sample name", "@name"),("[Al-26] / [Be-10]", "@y1")]))

    plot_script, plot_div = components(p)

    return components(p)

def get_shoreline():

    with open("static/world_shoreline.geojson", "r") as f:
        geojson_data = json.load(f)

    return GeoJSONDataSource(geojson=json.dumps(geojson_data))

def askiced_table(askiced_query):
    askiced_query = askiced_query
    askiced_result = dbconnect.querier_iced(askiced_query)
    
    data_table = tabulate(askiced_result, headers='firstrow', tablefmt='github', showindex=False)

    return data_table

def geo_map(app_id, path):
    app_id = app_id
    path = path

    shoreline = gpd.read_file("static/world_shoreline.geojson")

    shoreline_3412 = shoreline.to_crs("EPSG:3412")

    geo_source = GeoJSONDataSource(
        geojson=shoreline_3412.to_json()
    )

    core_query = f"""SELECT DISTINCT base_core.lat_DD, base_core.lon_DD, base_core.name
            FROM base_core
            JOIN base_sample ON base_sample.core_id = base_core.id
            JOIN base_sample_application ON base_sample.id = base_sample_application.sample_id
            WHERE base_sample_application.application_id = {app_id}"""
    
    list_result = dbconnect.querier_radci(core_query)

    y1 = list_result[1:,0].astype(float)
    x1 = list_result[1:,1].astype(float)
    name = list_result[1:,2]

    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:3412",
        always_xy=True
    )

    x, y = transformer.transform(x1, y1)

    data = {'lat': array(y),
            'lon': array(x),
            'name': array(name)}


    p = figure(width=1000, height=950, x_range=(-3000000, 3000000), y_range=(-3000000, 3000000),)
    p.patches(
        xs="xs",
        ys="ys",
        source=geo_source,
        fill_color="lightgray",
        fill_alpha=0.5,
        line_color="black"
    )
    scatter = p.scatter(x='lon',y='lat', source=data, size=20, fill_color= 'rgba(48, 92, 222, 1)', fill_alpha=0.9, line_color='grey', line_width=0.5)
    p.add_tools(HoverTool(renderers=[scatter], tooltips=[("Core name", "@name")]))
    p.axis.visible = False
    p.grid.visible = False

    plot_script, plot_div = components(p)

    return components(p)