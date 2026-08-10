from math import pi
from scipy.odr import ODR, Model, RealData
#from matplotlib.patches import Ellipse
import numpy as np
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import Span, HoverTool, ColorBar, LinearColorMapper, GeoJSONDataSource, Ellipse
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

import dbconnect

# Number of Monte Carlo simulations (recommend at least 1000)
MC_runs=1000

# Initialize variables
var_list = []
pretype=1
external_uncertainty=0
no_3sigma=1
MC_pt_plot=0
MC_line_plot=0
force_zero_pb=0
plot_inh=0

#initialize constants and such
const_list = []
tau10_mean = 2005000
tau26_mean = 1021000
Rsurf_mean = 6.8
Rpost_mean = 8.3
rho_mean = 2.65
Lambda_mean = 160
p10_SLHL_mean = 3.84
tau10_unc = 17000
tau26_unc = 24000
Rsurf_unc = 0.6
Rpost_unc = 0.8
rho_unc = 0.001
Lambda_unc = 10
p10_SLHL_unc = 0.27

# def minburial (Rmeas,erosion,age):
#     Rinh=Rsurf*((1/tau10+(rho*erosion)/Lambda)/(1/tau26+(rho*erosion)/Lambda))
#     age=taubur*np.log(Rinh/Rmeas)
#     erosion=(p10surf/np.exp(age/tau10)-n10meas/tau10)*(Lambda/(n10meas*rho))  
#     return age, erosion

def pysochron(burial_core, var_list, const_list):
    MC_runs = 1000
    var_list = var_list
    const_list = const_list

    burial_core = burial_core

    pretype=var_list[0].astype(float)
    external_uncertainty=var_list[1].astype(float)
    no_3sigma=var_list[2].astype(float)
    MC_pt_plot=var_list[3].astype(float)
    MC_line_plot=var_list[4].astype(float)
    force_zero_pb=var_list[5].astype(float)
    plot_inh=var_list[6].astype(float)

    tau10_mean = const_list[0].astype(float)
    tau26_mean = const_list[1].astype(float)
    Rsurf_mean = const_list[2].astype(float)
    Rpost_mean = const_list[3].astype(float)
    rho_mean = const_list[4].astype(float)
    Lambda_mean = const_list[5].astype(float)
    p10_SLHL_mean = const_list[6].astype(float)
    tau10_unc = const_list[7].astype(float)
    tau26_unc = const_list[8].astype(float)
    Rsurf_unc = const_list[9].astype(float)
    Rpost_unc = const_list[10].astype(float)
    rho_unc = const_list[11].astype(float)
    Lambda_unc = const_list[12].astype(float)
    p10_SLHL_unc = const_list[13].astype(float)

    query = f"""SELECT DISTINCT _be10_al26_quartz.N10_atoms_g, _be10_al26_quartz.delN10_atoms_g, _be10_al26_quartz.N26_atoms_g, _be10_al26_quartz.delN26_atoms_g, base_core.lat_DD, base_core.lon_DD, base_core.elv_m, base_coresample.top_depth_cm, base_coresample.name
        FROM base_core
        JOIN base_coresample ON base_core.id = base_coresample.core_id
        JOIN base_coresamplenuclidematch ON base_coresample.id = base_coresamplenuclidematch.coresample_id
        JOIN _be10_al26_quartz ON base_coresamplenuclidematch.be10_al26_quartz_id = _be10_al26_quartz.id
        WHERE base_core.name LIKE "%{burial_core}%"
        AND base_coresample.id != 940"""
    
    result = dbconnect.querier_iced(query)

    al26 = (result[1:,0])# / 1000000
    al26err = (result[1:,1])# / 1000000
    be10 = (result[1:,2])# / 1000000
    be10err = (result[1:,3])# / 1000000
    lat = result[1:,4]
    lon = result[1:,5]
    elv_m = result[1:,6]
    depth = result[1:,7]
    name = result[1:,8]

    #Al,Al unc,Be,Be unc,lat,elev_m,Sample ID
    #only headers we need even though the query gets more than that

    data = {
        'Al': np.array(al26),
        'Al unc': np.array(al26err),
        'Be': np.array(be10),
        'Be unc': np.array(be10err),
        'lat': np.array(lat),
        #'lon': np.array(lon),
        'elev_m': np.array(elv_m),
        #'depth': np.array(depth),
        'Sample ID': np.array(name)
    }

    lat=data['lat'].astype(float)
    elev_m=data['elev_m'].astype(float)

    # Extract measurements
    Al=data['Al'].astype(float)
    Al_unc=data['Al unc'].astype(float)
    Be=data['Be'].astype(float)
    Be_unc=data['Be unc'].astype(float)

    # Remove nans that may be present
    Al = Al[~np.isnan(Al)]
    Al_unc = Al_unc[~np.isnan(Al_unc)]
    Be = Be[~np.isnan(Be)]
    Be_unc = Be_unc[~np.isnan(Be_unc)]
    lat = lat[~np.isnan(lat)]
    elev_m = elev_m[~np.isnan(elev_m)]
        
    # Convert lat & elev_m to int for calculations
    lat=lat[0]
    elev_m=elev_m[0]

    # Calculate p10 at the locality.  The following code is modified directly from
    # stone2000.m, written by G. Balco and adopted to Python by W. Odom.
    P=1013.25*np.exp((-0.03417/0.0065)*(np.log(288.15)-np.log(288.15-0.0065*elev_m)))
    from scipy.interpolate import interp1d
    Fsp=0.978
    a = [31.8518, 34.3699, 40.3153, 42.0983, 56.7733, 69.0720, 71.8733]
    b = [250.3193, 258.4759, 308.9894, 512.6857, 649.1343, 832.4566, 863.1927]
    c = [-0.083393, -0.089807, -0.106248, -0.120551, -0.160859, -0.199252, -0.207069]
    d = [7.4260e-5, 7.9457e-5, 9.4508e-5, 1.1752e-4, 1.5463e-4, 1.9391e-4, 2.0127e-4]
    e = [-2.2397e-8, -2.3697e-8, -2.8234e-8, -3.8809e-8, -5.0330e-8, -6.3653e-8, -6.6043e-8]
    ilats = [0, 10, 20, 30, 40, 50, 60]

    # Neutrons
    latvals=[]
    latvals.append(a[0] + (b[0]* np.exp(P/(-150))) + (c[0]*P) + (d[0]*(P**2)) + (e[0]*(P**3)))
    latvals.append(a[1] + (b[1]* np.exp(P/(-150))) + (c[1]*P) + (d[1]*(P**2)) + (e[1]*(P**3)))
    latvals.append(a[2] + (b[2]* np.exp(P/(-150))) + (c[2]*P) + (d[2]*(P**2)) + (e[2]*(P**3))) 
    latvals.append(a[3] + (b[3]* np.exp(P/(-150))) + (c[3]*P) + (d[3]*(P**2)) + (e[3]*(P**3))) 
    latvals.append(a[4] + (b[4]* np.exp(P/(-150))) + (c[4]*P) + (d[4]*(P**2)) + (e[4]*(P**3))) 
    latvals.append(a[5] + (b[5]* np.exp(P/(-150))) + (c[5]*P) + (d[5]*(P**2)) + (e[5]*(P**3))) 
    latvals.append(a[6] + (b[6]* np.exp(P/(-150))) + (c[6]*P) + (d[6]*(P**2)) + (e[6]*(P**3))) 
    correction = np.zeros(1)
    lat = abs(lat)
    if lat>60:
        lat=60
    b =1;
    fs= interp1d(ilats,latvals)
    Ss=fs(lat)

    # Muons
    mk = [0.587, 0.600, 0.678, 0.833, 0.933, 1.000, 1.000]
    muvals=[]
    muvals.append(mk[0]*np.exp((1013.25-P)/242))
    muvals.append(mk[1]*np.exp((1013.25-P)/242))
    muvals.append(mk[2]*np.exp((1013.25-P)/242))
    muvals.append(mk[3]*np.exp((1013.25-P)/242))
    muvals.append(mk[4]*np.exp((1013.25-P)/242))
    muvals.append(mk[5]*np.exp((1013.25-P)/242))
    muvals.append(mk[6]*np.exp((1013.25-P)/242))
    fm= interp1d(ilats,muvals)
    Sm=fm(lat)
    scalingfactor = (Ss*Fsp)+(1-Fsp)*Sm

    # Generate seeds for curve_fit
    m,b = np.polyfit(Be,Al, 1)

    # Convert data to ODR-friendly format
    data=RealData(Be,Al,Be_unc,Al_unc)

    # Define preburial erosion
    if pretype == 1:
        def objective (Beta,n10):
            if force_zero_pb==1:
                Beta[0]=0
            return (n10-Beta[0])*(Rsurf)*((1/tau10+(rho*(((p10surf*np.exp(-Beta[1]/tau10))/(n10-Beta[0])-1/tau10)*(Lambda/rho)))/Lambda)/(1/tau26+(rho*(((p10surf*np.exp(-Beta[1]/tau10))/(n10-Beta[0])-1/tau10)*(Lambda/rho)))/Lambda))*np.exp(-Beta[1]/taubur)+(Beta[0]*tau26*Rpost*(1-np.exp(-Beta[1]/tau26)))/(tau10*(1-np.exp(-Beta[1]/tau10)))
        
    # Define preburial exposure
    if pretype == 0: 
        def objective (Beta,n10):
            if force_zero_pb==1:
                Beta[0]=0
            return (n10-Beta[0])*(Rsurf)*(tau26/tau10)*((1-np.exp(-(tau10*np.log(1-((n10-Beta[0])*np.exp(Beta[1]/tau10))/(p10surf*tau10)))/tau26))/(1-np.exp(-(tau10*np.log(1-((n10-Beta[0])*np.exp(Beta[1]/tau10))/(p10surf*tau10)))/tau10)))*np.exp(-Beta[1]/taubur)+(Beta[0]*tau26*Rpost*(1-np.exp(-Beta[1]/tau26)))/(tau10*(1-np.exp(-Beta[1]/tau10)))

    # Set up orthogonal distance regression, solve using least squares
    model=Model(objective)

    # Define x-axis of isochron and set axis limitations
    Be_step=max(Be)*1.5/250
    n10axis = np.arange(0.1,max(Be)*15,Be_step)
    # fig=plt.figure(dpi=1200)
    # ax = plt.gca()
    # ax.set_xlim([0, 1.2*max(Be)])
    # ax.set_ylim([0, 1.2*max(Al)])
    # ax = plt.gca()

    p = figure(title=f"{burial_core} Burial Isochron", width=855, height=540, x_axis_label="[$^1$$^0$Be] (at/g)", y_axis_label="[$^2$$^6$Al] (at/g)", tools="pan,wheel_zoom,save,reset", x_range=(0, (1.2*max(Be))), y_range=(0, 1.2*max(Al)))

    # Use mean values if external uncertainty is being ignored
    if external_uncertainty==0:
        Rsurf=Rsurf_mean       
        Rpost=Rpost_mean 
        tau10=tau10_mean
        tau26=tau26_mean
        rho=rho_mean
        Lambda=Lambda_mean
        p10_SLHL=p10_SLHL_mean
        p10surf=p10_SLHL*scalingfactor
        
    # Set up empty variables
    Al_MC=np.zeros(len(Al))
    Be_MC=np.zeros(len(Al))
    n26model_dist=[]
    n10pb_dist=[]
    t_dist=[]
    p10surf_dist=[]
    count=0
    failcount=0
    negativepbcount=0

    # Define stopping limit of MC simulations
    countmax=10**6

    # Start count of all MC simulations
    MC_count=0

    for i in range(countmax):
        MC_count=MC_count+1
        # Randomize external constants if desired
        if external_uncertainty==1:
            Rsurf=Rsurf_mean+np.random.randn()*Rsurf_unc
            Rpost=Rpost_mean+np.random.randn()*Rpost_unc
            tau10=tau10_mean+np.random.randn()*tau10_unc
            tau26=tau26_mean+np.random.randn()*tau26_unc
            rho=rho_mean+np.random.randn()*rho_unc
            Lambda=Lambda_mean+np.random.randn()*Lambda_unc 
            p10_SLHL=p10_SLHL_mean+np.random.randn()*p10_SLHL_unc
            p10surf=p10_SLHL*scalingfactor
            p10surf_dist.append(p10surf)
        taubur=1/(1/tau26-1/tau10) 
        
        # Generate initial inputs for model
        t_init=abs(taubur*np.log(m/Rsurf)*np.random.randn())
        n10pb_init=abs(min(Be)+min(Be)*np.random.randn())
        beta0=[n10pb_init,t_init]  
        n26model=[]
        for j in range(len(Al)):
            Al_MC[j]=Al[j]+Al_unc[j]*np.random.randn()
            Be_MC[j]=Be[j]+Be_unc[j]*np.random.randn()
            
        # Run ODR model
        data=RealData(Be_MC,Al_MC,Be_unc,Al_unc)
        odr = ODR(data, model,beta0)
        odr.set_job(fit_type=0)
        output_MC = odr.run()
        n26model=objective(output_MC.beta,n10axis)

        # Ignore result if burial age is 10x the half-life of 10Be
        if output_MC.beta[1]>10*np.log(2)*tau10:
            continue

        # Ignore result if negative age is generated
        if output_MC.beta[1]<0:
            continue

        # Ignore result if negative postburial present
        if output_MC.beta[0]<0:
            negativepbcount=negativepbcount+1
            continue

        # Calculate derivative of isochron line
        dydx=[]
        for j in range(len(n26model)):
            dydx.append((n26model[j]-n26model[j-1])/Be_step)
        del dydx[0]
        
        # Eliminate any lines with slope greater than surface P26/P10 (rare)
        # Eliminate any lines with negative slope (rare)
        # Save results of successful MC run and count towards 1000 MC runs
        if all(j <= (Rsurf_mean+Rsurf_unc) for j in dydx) and all(j >= 0 for j in dydx):         
            #plots every MC simulation if enabled
            if MC_line_plot==1:
                p.plot(n10axis,n26model,'blue',linewidth=0.25,alpha=0.25)     
            if MC_pt_plot==1:
                p.scatter(Be_MC,Al_MC,marker='.',color='k',s=0.25,alpha=0.5)
            n26model_dist.append(n26model)
            n10pb_dist.append(output_MC.beta[0])
            t_dist.append(output_MC.beta[1])
            count=count+1
            
        # Ignore spurious fit and record failed fit
        else:
            failcount=failcount+1
        
        # Halt loop if the desired number of successful runs has been completed
        if count==MC_runs:
            #print('|##########| 100% done') 
            break

        # Halt loop if failed fits is high relative to nonzero successful fits
        if failcount>(100*count) and count>1:
            #print('*****************************')
            #print('*    MAJOR FITTING ISSUES   *')
            #print('*        CODE HALTED        *')
            #print('*****************************')
            break
    
        # Halt loop if there are 1000 failed fits and zero successful fits
        if failcount==1000 and count==0:
            #print('*****************************')
            #print('*    MAJOR FITTING ISSUES   *')
            #print('*        CODE HALTED        *')
            #print('*****************************')
            break

    n26model_dist0=n26model_dist    
    n26model_mean=[]
    n26model_std=[]
    n26model_min=[]
    n26model_max=[]
    n26model_2min=[]
    n26model_2max=[]

    # Remove 3sigma outliers from dataset
    # Plots outlier lines in red if all MC lines are being plotted
    culled=0
    t_dist_culled=[]
    n10pb_dist_culled=[]
    n26model_dist_culled=[]
    if no_3sigma==1:

        # Plot 3-sigma outlier lines in red
        for i in range(len(t_dist)):
            if t_dist[i]>(np.mean(t_dist)+3*np.std(t_dist)) or t_dist[i]<(np.mean(t_dist)-3*np.std(t_dist)) or n10pb_dist[i]>(np.mean(n10pb_dist)+3*np.std(n10pb_dist)) or n10pb_dist[i]<(np.mean(n10pb_dist)-3*np.std(n10pb_dist)):
                if MC_line_plot==1:
                    p.plot(n10axis,n26model_dist0[i],'red',linewidth=0.25,alpha=1)
        
        # Remove 3-sigma t_dist and n10pb_dist outliers
        for i in range(len(t_dist)):
            if t_dist[i]<=(np.mean(t_dist)+3*np.std(t_dist)) and t_dist[i]>=(np.mean(t_dist)-3*np.std(t_dist)) and n10pb_dist[i]<=(np.mean(n10pb_dist)+3*np.std(n10pb_dist)) and n10pb_dist[i]>=(np.mean(n10pb_dist)-3*np.std(n10pb_dist)):
                t_dist_culled.append(t_dist[i])
                n10pb_dist_culled.append(n10pb_dist[i])
                n26model_dist_culled.append(n26model_dist[i])            
        t_dist=t_dist_culled
        n10pb_dist=n10pb_dist_culled
        culled=MC_runs-len(t_dist)
        n26model_dist=n26model_dist_culled
    n26model_dist=np.transpose(n26model_dist)  

    # Generate mean isochron line and error envelope
    for i in range(len(n10axis)):
        n26model_mean.append(np.mean(n26model_dist[i]))
        n26model_std.append(np.std(n26model_dist[i]))
        n26model_min.append(n26model_mean[i]-n26model_std[i])
        n26model_max.append(n26model_mean[i]+n26model_std[i])
        n26model_2min.append(n26model_mean[i]-2*n26model_std[i])
        n26model_2max.append(n26model_mean[i]+2*n26model_std[i])
    if MC_line_plot==0:
        #ax.fill_between(n10axis, n26model_2min, n26model_2max, color='lightsteelblue',linewidth=0, alpha=0.25) 
        #ax.fill_between(n10axis, n26model_min, n26model_max, color='lightsteelblue',linewidth=0, alpha=0.5) 
        p.plot(n10axis,n26model_mean,color='black',linewidth=0.5)

    # Plot sample error ellipses
    if MC_pt_plot==0:
        for i in range(len(Be)):
            u=Be[i]   
            v=Al[i]   
            a=Be_unc[i]   
            b=Al_unc[i]  
            t = np.linspace(0, 2*pi, 100)
            p.plot( u+a*np.cos(t) , v+b*np.sin(t),color='black',linewidth=0.5,zorder=101)
            if MC_line_plot==1:
                # ell = Ellipse(xy=[u,v], width=a*2, height=b*2, angle=0,
                #         edgecolor='none', lw=4, facecolor='white',alpha=0.75,zorder=100)
                p.add_glyph(Ellipse(x=u,
                          y=v,
                          width=a*2,
                          height=a*2,
                          angle=0,
                          line_width=4)
                )
            else:
                # ell = Ellipse(xy=[u,v], width=a*2, height=b*2, angle=0,
                #     edgecolor='none', lw=4, facecolor='white',alpha=0.5,zorder=100)
                p.Ellipse(x=u,
                          y=v,
                          width=a*2,
                          height=a*2,
                          angle=0,
                          line_width=4)
            # ax.add_artist(ell)

    # Label isochron axes
    #plt.xlabel("[$^1$$^0$Be] (at/g)")
    #plt.ylabel("[$^2$$^6$Al] (at/g)")

    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    #plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))    

    # Calculate MSWD
    data_MSWD=RealData(Be,Al,Be_unc,Al_unc)
    odr_MSWD = ODR(data_MSWD, model,beta0)
    odr.set_job(fit_type=0)
    output_MSWD = odr_MSWD.run()

    t_mean=np.mean(t_dist)
    t_unc=np.std(t_dist)

    def minburial (Rmeas,erosion,age):
        Rinh=Rsurf*((1/tau10+(rho*erosion)/Lambda)/(1/tau26+(rho*erosion)/Lambda))
        age=taubur*np.log(Rinh/Rmeas)
        erosion=(p10surf/np.exp(age/tau10)-n10meas/tau10)*(Lambda/(n10meas*rho))  
        return age, erosion

    simpleflags=0
    min_ages=[]
    min_ages_unc=[]
    simple_erosion=[]
    simple_erosion_unc=[]

    # Calculate minimum burial age for each sample
    for i in range(len(Al)): 
        simple_dist=[]     
        erosion_dist=[]
        
        # 1000 run MC calculation
        for j in range(1000):
            n26meas=Al[i]+Al_unc[i]*np.random.randn()
            n10meas=Be[i]+Be_unc[i]*np.random.randn()
            age=t_mean
            erosion=5/10000
            Rmeas=n26meas/n10meas
            simple_age=minburial(Rmeas,erosion,age)
            simple_dist.append(simple_age[0])
            erosion_dist.append(simple_age[1])
            
        # Note if a given sample has a minimum age exceeding isochron age
        if (np.mean(simple_dist)-2*np.std(simple_dist))>(t_mean+2*t_unc):
                #print('\u2718 Sample',i+1,'has minimum age greater than the isochron age.')
                simpleflags=simpleflags+1
                
        min_ages.append(np.mean(simple_dist))
        min_ages_unc.append(np.std(simple_dist))
        simple_erosion.append(np.mean(erosion_dist)*10**4)
        simple_erosion_unc.append(np.std(erosion_dist)*10**4)
    
    fmin= interp1d(n10axis,n26model_2min)
    fmax= interp1d(n10axis,n26model_2max)
    fmean=interp1d(n10axis,n26model_mean)
    flag_count=0

    for i in range(len(Be)):
        lower=0
        upper=0
        flags=0
        
        # Calculate upper and lower misfits
        lower= fmin(Be[i])-(Al[i]+2*Al_unc[i])
        upper= (Al[i]-2*Al_unc[i]) - fmax(Be[i])    
        
        # If Al measurement is BELOW a 2-sigma overlap, note it
        if lower>0:
            #print('\u2718 Sample',i+1,'below isochron line.')
            if MC_pt_plot==0:
                u=Be[i]   
                v=Al[i]   
                a=Be_unc[i]   
                b=Al_unc[i]  
                t = np.linspace(0, 2*pi, 100)       
                # ell = Ellipse(xy=[u,v], width=a*2, height=b*2, angle=0,
                #         edgecolor='none', lw=4, facecolor='none')
                # ax.add_artist(ell)
                p.Ellipse(x=u,
                          y=v,
                          width=a*2,
                          height=a*2,
                          angle=0,
                          line_width=4)
                p.plot(u+a*np.cos(t) , v+b*np.sin(t),color='red',linewidth=0.5,zorder=101)
                flags=flags+1
                
        # If Al measurement is ABOVE a 2-sigma overlap, note it
        if upper>0:
            #print('\u2718 Sample',i+1,'above isochron line.')
            flags=flags+1
        flag_count=flag_count+flags

    # if plot_inh==0:
    #     ax.set_xlim([0, 1.2*max(Be)])
    #     ax.set_ylim([0, 1.2*max(Al)])

    # # Plot inherited isochron line if selected
    # if plot_inh==1:    
    #     n26inh_line=np.zeros(len(n10axis))
    #     if pretype==1: 
    #         for i in range(len(n10axis)):
    #             n26inh_line[i]=n10axis[i]*Rsurf*((1/tau10+(rho*(p10surf-n10axis[i]/tau10)*(Lambda/(rho*n10axis[i])))/Lambda)/(1/tau26+(rho*(p10surf-n10axis[i]/tau10)*(Lambda/(rho*n10axis[i])))/Lambda))
    #     if pretype==0: 
    #         for i in range(len(n10axis)):
    #             n26inh_line[i]=(n10axis[i]*Rsurf*tau26*(1-np.exp(-(-tau10*np.log(1-n10axis[i]/(p10surf*tau10)))/tau26)))/(tau10*(1-np.exp(-(-tau10*np.log(1-n10axis[i]/(p10surf*tau10)))/tau10)))
    #     plt.plot(n10axis,n26inh_line,'--k',linewidth=0.5,zorder=151)

    # Display inputs, constants, and results below isochron plot
    max_Al=max(Al)
    max_Be=max(Be)

    plot_script, plot_div = components(p)

    return components(p)