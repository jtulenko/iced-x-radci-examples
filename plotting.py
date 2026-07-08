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