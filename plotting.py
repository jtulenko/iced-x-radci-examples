from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import Span, HoverTool, ColorBar, LinearColorMapper, GeoJSONDataSource
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.palettes import Viridis256
import pandas
import numpy 
from numpy import array, log, tan, pi
#import xyzservices.providers as xyz
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import xarray as xr
import netCDF4 as nc
#import gcsfs
#import zarr
#import dask
import geopandas as gpd
import json
from cmcrameri import cm
import gc

import dbconnect

def rsl_plot(rsl_plot):
    rsl_plot = rsl_plot

    rsl_plot_query = f"""SELECT base_sample.name, base_calibratedage.age_calyrBP, base_calibratedage.minage_1sd_calyrBP, maxage_1sd_calyrBP, base_rsl_info.sealevel_index_elev_m, base_rsl_info.sealevel_index_elev_m_err
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
	    AND base_application_sites.application_id = 1"""
    
    list_result = dbconnect.querier_iced(c14_psat_query)

    x1 = (list_result[1:,0].astype(float)) * 0.00012096809
    y1 = list_result[1:,1].astype(float)
    sizes = (list_result[1:,2].astype(float)) ** (1/4)
    name = list_result[1:,3]

    #df1 = pandas.DataFrame(list(result))
    #x1 = df1[0] * 0.00012096809
    #y1 = df1[1]
    #sizes = df1[2] ** (1/4)
    #name = df1[3]

    data = {'x1': array(x1),
                'y1': array(y1),
                'sizes': array(sizes),
                'name': array(name)}

    p= figure(width=750, height=500, x_axis_type="log", title="Saturation concentration of in-situ C-14")
    p.xaxis.axis_label = "N * I"
    p.yaxis.axis_label = "Elevation (m)"

    p.scatter('x1','y1', size='sizes', source=data, fill_color='rgba(255, 168, 38, 1)', fill_alpha=0.9, line_color='grey', line_alpha=0.1, marker="circle")
    p.add_tools(HoverTool(tooltips=[("Sample name", "@name"),("Age (ka)", "@sizes"),("N * I", "@x1")]))


    plot_script, plot_div = components(p)

    return components(p)

def get_shoreline():

    with open("static/world_shoreline.geojson", "r") as f:
        geojson_data = json.load(f)

    return GeoJSONDataSource(geojson=json.dumps(geojson_data))

def get_rsl_input(rsl_input):
    rsl_input = rsl_input
    if rsl_input == "aust21VM":
        path = 'gs://giamachine_output_data/SL_austermann2021/austermann2021_RSL_VM.zarr'
        plot_title = 'Austermann et al. (2021) VM'
    elif rsl_input == "aust21p5":
        path = 'gs://giamachine_output_data/SL_austermann2021/austermann2021_RSL_p5.zarr'
        plot_title = 'Austermann et al. (2021) p5'
    elif rsl_input == "aust22LAM_PC":
        path = 'gs://giamachine_output_data/SL_austermann2022/austermann2022_LAM_PC_pcd.zarr'
        plot_title = 'Austermann et al. (2022) LAM PC'
    elif rsl_input == 'creel24_a':
        path = 'gs://giamachine_output_data/SL_creel24/SL_creel2024_400k_3k_rcp2p6_ch21exp07_gr21exp07_l90C.umVM5.lmVM5_UPDATED.zarr'
        plot_title = 'Creel et al. (2024) a'

    ds = xr.open_zarr(path, consolidated=True, chunks={})
    
    # if ds['lon'].max() > 180:
    #     lon_converted = ds['lon'] - 180
    #     ds = ds.assign_coords(lon=lon_converted)
    #     ds = ds.sortby('lon')

    # rounded_lat = numpy.round(ds['lat'].values).astype(int)
    # rounded_lon = numpy.round(ds['lon'].values).astype(int)

    # ds = ds.assign_coords(lat_rounded=("lat", rounded_lat), lon_rounded=("lon", rounded_lon))
    # ds = ds.groupby('lat_rounded').mean()
    # ds = ds.groupby('lon_rounded').mean()

    # ds = ds.rename({'lat_rounded': 'lat', 'lon_rounded': 'lon'})

    return ds, plot_title

################################################################################

def sealevel_plot1(lat_min, lat_max, lon_min, lon_max, age_value, rsl_recon, rsl_max, rsl_min):
    rsl_input = rsl_recon
    shoreline = get_shoreline()
    ds, plot_title = get_rsl_input(rsl_input)
    age_array = ds['age'].values
    lat_array = ds['lat'].values
    lon_array = ds['lon'].values

    age_idx = numpy.abs(age_array - age_value).argmin()
    age_value_closest = age_array[age_idx]

    rsl_max = rsl_max
    rsl_min = rsl_min

    #this all got annoying because the stupid plot listed lons in 0-360 instead of -180-180
    #the fix seems convoluted so I might try again. UGHHHHHHHHHH
    # lon_fix = []
    
    # for i in lon_array:
    #     if lon_array >= 0:
    #         lon_temp = lon_array[i] - 180
    #         lon_fix.append(lon_temp)
    #     if lon_array <= 0:
    #         lon_temp = lon_array[i] + 180
    #         lon_fix.append(lon_temp)

    if age_value in age_array and lat_min in lat_array and lat_max in lat_array and lon_min in lon_array and lon_max in lon_array:
        map_bounds = ds.sel(
            age=age_value,
            lat=slice(int(lat_min), int(lat_max)),
            lon=slice(int(lon_min), int(lon_max))
        )
    else:
        map_bounds = ds.sel(
            age=float(age_value_closest),
            lat=slice(int(lat_min), int(lat_max)),
            lon=slice(int(lon_min), int(lon_max))
        )
        #raise ValueError(f"Time Slice not available for selected simulation, {age_value_closest} {lat_min_closest} {lat_max_closest} {lon_min_closest} {lon_max_closest} {lon_min_idx}, {lon_max_idx}")

    if '(2021)' in plot_title:
        data_plot = map_bounds['RSL_VM5_1D'].values.transpose(1,0)
    elif '(2022)' in plot_title:
        data_plot = map_bounds['rsl'].values.transpose(1,0)
    else:
        data_plot = map_bounds['change_in_mean_sea_level_due_to_change_in_geoid_and_solid_earth_deformation'].values.transpose(1,0)

    if numpy.isnan(data_plot).all():
        raise ValueError("All values in data_plot are NaN.")
    
    cmap = cm.batlow
    n_colors = 256
    hex_colors = [mcolors.rgb2hex(cmap(i / (n_colors - 1))) for i in range(n_colors)]

    #color_mapper = LinearColorMapper(palette=hex_colors, low=numpy.nanmin(data_plot), high=numpy.nanmax(data_plot))
    color_mapper = LinearColorMapper(palette=hex_colors, low=rsl_min, high=rsl_max)

    p = figure(title=f"{plot_title}, Age Slice = {round(age_value_closest, 0)} ka", width=855, height=540, x_axis_label="Longitude", y_axis_label="Latitude", tools="pan,wheel_zoom,save,reset", x_range=(lon_min, lon_max), y_range=(lat_min, lat_max))
    p.image(image=[data_plot], x=lon_min, y=lat_min, dw=lon_max - lon_min, dh=lat_max - lat_min, color_mapper=color_mapper)
    p.patches('xs', 'ys', source=shoreline, fill_alpha=0, fill_color = 'black', line_color='black', line_width=1.75)
    p.add_layout(ColorBar(color_mapper=color_mapper, title='Relative Sea Level (m)', title_text_baseline='middle', title_text_align='center', title_text_font_style='bold'), 'left')

    plot_script, plot_div = components(p)
    
    del data_plot
    del shoreline
    gc.collect()

    return components(p)

def sealevel_ts(lat, lon, age_min, age_max, rsl_recon):
    rsl_input = rsl_recon
    ds, plot_title = get_rsl_input(rsl_input)
    
    lat = int(lat)
    lon = int(lon)
    age_min = age_min
    age_max = age_max

    if '(2021)' in plot_title:
        rsl_data = ds['RSL_VM5_1D'][:, lat, lon].values
    elif '(2022)' in plot_title:
        rsl_data = ds['rsl'][:, lat, lon].values
    else:
        rsl_data = ds['change_in_mean_sea_level_due_to_change_in_geoid_and_solid_earth_deformation'][:, lat, lon].values
    age_data = ds['age'].values

    p = figure(title=f"{plot_title}, at degrees {lat}, {lon}", width=855, height=540, x_axis_label="Age (ka)", y_axis_label="Relative Sea Level (m)", tools="pan,wheel_zoom,save,reset", x_range=(age_max, age_min))
    p.scatter(x=age_data, y=rsl_data, size=3, color='navy', alpha=0.4)
    p.line(x=age_data, y=rsl_data, line_width=2, color='navy', alpha=1)

    plot_script, plot_div = components(p)

    del rsl_data
    del age_data
    gc.collect()

    return components(p)

def get_vvel_input(vdef_input):
    vdef_input = vdef_input
    # if vdef_input == "drad_D1":
    #     path = 'gs://giamachine_output_data/velocity/drad_D1.zarr'
    #     plot_title = 'Check with Holger'
    if vdef_input == "drad_ICE5Gv1.3VM2L90":
        path = 'gs://giamachine_output_data/velocity/drad_ICE5Gv1.3VM2L90.zarr'
        plot_title = 'ICE5G v1.3 VM2 L90 vertical velocity solution (mm/yr)'
    if vdef_input == "drad_ICE6GCVM5a":
        path = 'gs://giamachine_output_data/velocity/drad_ICE6GCVM5a.zarr'
        plot_title = 'ICE6G CVM5a vertical velocity solution (mm/yr)'
    if vdef_input == "drad_ICE6GDVM5a":
        path = 'gs://giamachine_output_data/velocity/drad_ICE6GDVM5a.zarr'
        plot_title = 'ICE6G DVM5a vertical velocity solution (mm/yr)'
    if vdef_input == "drad_LM17.3":
        path = 'gs://giamachine_output_data/velocity/drad_LM17.3.zarr'
        plot_title = 'LM 17.3 vertical velocity solution (mm/yr)'

    ds = xr.open_zarr(path, consolidated=True, chunks={})

    return ds, plot_title


def vvel_plot1(lat_min, lat_max, lon_min, lon_max, vdef_recon, vdef_max, vdef_min):
    vdef_input = vdef_recon
    shoreline = get_shoreline()
    ds, plot_title = get_vvel_input(vdef_input)
    lat_array = ds['lat'].values
    lon_array = ds['lon'].values

    vdef_max = vdef_max
    vdef_min = vdef_min
    
    if lat_min in lat_array and lat_max in lat_array and lon_min in lon_array and lon_max in lon_array:
        map_bounds = ds.sel(
            lat=slice(int(lat_min), int(lat_max)),
            lon=slice(int(lon_min), int(lon_max))
        )
    else:
        map_bounds = ds.sel(
            lat=slice(int(lat_min), int(lat_max)),
            lon=slice(int(lon_min), int(lon_max))
        )
        #raise ValueError(f"Time Slice not available for selected simulation, {age_value_closest} {lat_min_closest} {lat_max_closest} {lon_min_closest} {lon_max_closest} {lon_min_idx}, {lon_max_idx}")

    #data_plot = map_bounds['Drad'].values.transpose(1,0)
    data_plot = map_bounds['Drad'].values

    if numpy.isnan(data_plot).all():
        raise ValueError("All values in data_plot are NaN.")
    
    cmap = cm.batlow
    n_colors = 256
    hex_colors = [mcolors.rgb2hex(cmap(i / (n_colors - 1))) for i in range(n_colors)]

    #color_mapper = LinearColorMapper(palette=hex_colors, low=numpy.nanmin(data_plot), high=numpy.nanmax(data_plot))
    color_mapper = LinearColorMapper(palette=hex_colors, low=vdef_min, high=vdef_max)

    p = figure(title=f"{plot_title}", width=855, height=540, x_axis_label="Longitude", y_axis_label="Latitude", tools="pan,wheel_zoom,save,reset", x_range=(lon_min, lon_max), y_range=(lat_min, lat_max))
    p.image(image=[data_plot], x=lon_min, y=lat_min, dw=lon_max - lon_min, dh=lat_max - lat_min, color_mapper=color_mapper)
    p.patches('xs', 'ys', source=shoreline, fill_alpha=0, fill_color = 'black', line_color='black', line_width=1.75)
    p.add_layout(ColorBar(color_mapper=color_mapper, title='Vertical velocity (mm/yr)', title_text_baseline='middle', title_text_align='center', title_text_font_style='bold'), 'left')

    plot_script, plot_div = components(p)

    del data_plot
    del shoreline
    gc.collect()

    return components(p)