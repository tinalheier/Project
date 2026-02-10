import numpy as np
from emphererides_file import read_rinex_file
import datetime
import pandas as pd


GM = 3.986005 * 10**14
omega_e = 7.2921151467 * 10**(-5)
pi = np.pi

def find_satellites(df, date, observation_time):  
    rows =[]
    positions_list = []

    t_obs = observationTime(date, observation_time)   
    df_sorted = df.sort_values(['sat','toe']) 
    sats = sorted(df['sat'].unique())
    df['toe'] = pd.to_numeric(df['toe'], errors='coerce')



    for satname in sats:
        
        onlySpesificSatRows = df[df['sat'] == satname]

    
        underOrEqual  = onlySpesificSatRows[onlySpesificSatRows['toe'] <= t_obs]
       

        if not underOrEqual.empty:
            row = (t_obs - underOrEqual['toe']).abs().idxmin()
            closest_row = df.loc[row]
            rows.append(closest_row)
        
        else: 
            row = (onlySpesificSatRows['toe'] - t_obs).abs().idxmin()
            closest_row = df.loc[row]
            rows.append(closest_row)

    
    df_with_satellites_for_time = pd.DataFrame(rows)

    for index, row in df_with_satellites_for_time.iterrows():

        sat, epoch = row['sat'], row['epoch']

        positions = findPosition(df_with_satellites_for_time, sat, epoch, observation_time)
        positions_list.append(positions)
   
    df_with_satellites_for_time['satellitePosition'] = positions_list

 
    return df_with_satellites_for_time



def findPosition(df, sat, epoch, observationtime):
  
    row = df.loc[(df["sat"] == sat) & (df["epoch"] == epoch)]

    row_data = row.squeeze() 
    UTC_time = str(row_data["UTC_time"])
    Crs = float(row_data["Crs"])
    delta_n = float(row_data["Delta_N"])
    Cuc = float(row_data["Cuc"])
    M0 = float(row_data["M0"])
    Cus = float(row_data["Cus"])
    e = float(row_data["e"])
    toe = float(row_data["toe"])
    Cic = float(row_data["Cic"])
    a_sqrt = float(row_data["a_sqrt"])
    lambda0 = float(row_data["lambda0"])
    Cis = float(row_data["Cis"])
    i0 = float(row_data["i0"])
    Crc = float(row_data["Crc"])
    omega = float(row_data["omega"])
    OMEGA_dot = float(row_data["OMEGA_dot"])
    i_dot_dot = float(row_data["i_dotdot"])

    obstime = observationTime(epoch, observationtime)

    transtime = transmissionTime(obstime)
    tk_value = tk(toe, transtime)


    Mk_value = Mk(tk_value, M0, a_sqrt, delta_n)

    Ek_value = Ek(Mk_value, e)

    fk_value = fk(e,Ek_value)
    
    u_k = omega + fk_value + (Cuc * np.cos( 2 * (omega + fk_value))) + (Cus * np.sin( 2 * (omega + fk_value)))
    r_k = a_sqrt**2 * (1 - (e * np.cos(Ek_value))) + (Crc* np.cos(2 * (omega + fk_value))) + (Crs * np.sin(2*(omega + fk_value)))
    i_k = i0 + (i_dot_dot * tk_value) + (Cic * np.cos( 2 * (omega + fk_value))) + (Cis * np.sin( 2 * (omega + fk_value)))
    lamda_k = lambda0 + ((OMEGA_dot- omega_e)*tk_value) - (omega_e * toe)
            
    
    coord = rotation_matrix(-lamda_k)[2] @  rotation_matrix(-i_k)[0] @ rotation_matrix(-u_k)[2] @ np.array([r_k, 0, 0])
    
    return coord


def observationTime(epoch, obstime):
    year = int(epoch[0:4])
    
    if epoch[4] == "0":
        month = int(epoch[5])
    else: month = int(epoch[4:6])

    if epoch[6] == "0":
        date = int(epoch[7])
    else: date = int(epoch[6:8])
    
    dateis = datetime.date(year, month, date)  
    
    dayOfWeek = dateis.strftime("%A")  
    
    hour = int(obstime[0:2]) * 60 * 60
    minutes = int(obstime[2:4]) * 60
    seconds = int(obstime[4:6])


    if dayOfWeek == "Monday":
        secs = 86400
        obstime = secs + hour + minutes + seconds

    elif dayOfWeek == "Tuesday":
        secs = 172800
        obstime = secs + hour + minutes + seconds
    
    elif dayOfWeek == "Wednesday":
        secs = 259200
        obstime = secs + hour + minutes + seconds
    
    elif dayOfWeek == "Thursday":
        secs = 345600
        obstime = secs + hour + minutes + seconds
    
    elif dayOfWeek == "Friday":
        secs = 432000
        obstime = secs + hour + minutes + seconds
    
    elif dayOfWeek == "Saturday":
        secs = 518400

        obstime = secs + hour + minutes + seconds

    elif dayOfWeek == "Sunday":
        secs = 0
        obstime = secs + hour + minutes + seconds
    
    else: 
        print("Day doesn't exist")

    return obstime

def transmissionTime(observation_time):
    return observation_time - 0.066

    
def tk(toe, transtime): 
    tk_value = transtime - toe

    if tk_value < -302400:
        return  tk_value + 604800
    elif tk_value > 302400:
        return  tk_value - 604800
    
    else: return tk_value

def Mk(tk, M0, a_sqrt, delta_n):
    return M0 + tk * (np.sqrt(GM / a_sqrt**6) + delta_n)

def Ek(Mk,e):
    Ej = Mk

    for i in range(3):
            Ej = Ej + ((Mk - Ej + e * np.sin(Ej))) / (1 - (e * np.cos(Ej)))

    return Ej

def fk(e,Ek):
    return 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(Ek/2))



def rotation_matrix(degree):
    rot_1 = np.array([[1,0,0],
                     [0, np.cos(degree), np.sin(degree)],
                     [0, -np.sin(degree), np.cos(degree)]])
    
    rot_2 = np.array([[np.cos(degree), 0, -np.sin(degree)], 
                     [0, 1, 0],
                     [np.sin(degree), 0, np.cos(degree)]])
    
    rot_3 = np.array([[np.cos(degree), np.sin(degree), 0], 
                     [-np.sin(degree), np.cos(degree), 0],
                     [0, 0, 1]])
 
    return rot_1, rot_2, rot_3





