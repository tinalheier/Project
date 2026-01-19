import numpy 
import pandas as pd
import os

def read_rinex_file(filename):
    Galileo = []
    GPS = []
    GLONASS = []
    BeiDou = []

    with open(filename, "r") as file:
        lines = file.readlines()

        
        start_idx = [i for i, l in enumerate(lines) if "END OF HEADER" in l][0]+1
        i = start_idx
    
        
        while i < len(lines):
    

            line =  lines[i].strip()

            satellitename = line[0:3] 
            year = line[4:8]
            month  = line[9:11]
            date = line[12:14]
            
            UTC_clock = line[15:17] + line[18:20] + line[21:23]  #Klokken 23:40:29 = 234029
            yearmonthdate = year + month + date  #22.AUG 2025 = 20250822

            if line.startswith("G"):
                

                
                block = lines[i:i+8]
           
                j = 0
                for b in block:
                    split = split_rinex_line(b)    
                    
                    if j == 1:
                        Crs = float(split[1]) 
                        Delta_N = float(split[2]) 
                        M0 = float(split[3]) 
                      
                    elif j == 2:
                        Cuc = (split[0]) 
                        e = float(split[1])
                        Cus = float(split[2]) 
                        a_sqrt = float(split[3]) 
                     
                    elif j == 3:
                        toe = (split[0]) 
                        Cic = float(split[1]) 
                        lambda0 = float(split[2]) 
                        Cis = float(split[3]) 
                   
                   

                    elif j == 4:
                        i0 = (split[0]) 
                        Crc = float(split[1]) 
                        omega = float(split[2]) 
                        OMEGA_dot = float(split[3]) 
                   

                    elif j == 5:
                        i_dotdot = (split[0]) 
                    j += 1
                
                GPS.append({
                    "system": "GPS",
                    "sat": satellitename,
                    "epoch": yearmonthdate,
                    "UTC_time": UTC_clock,
                    "Crs": Crs,
                    "Delta_N": Delta_N,
                    "Cuc": Cuc,
                    "M0": M0,
                    "Cus": Cus,
                    "e": e,
                    "a_sqrt": a_sqrt,
                    "toe": toe,
                    "Cic": Cic,
                    "lambda0": lambda0,
                    "Cis": Cis,
                    "i0": i0,
                    "Crc": Crc,
                    "omega": omega,
                    "OMEGA_dot": OMEGA_dot,
                    "i_dotdot": i_dotdot
                })
                                    
                i +=8



            elif line.startswith("R"):
                block = lines[i:i+4]

                j = 0
                for b in block:
                    split = split_rinex_line(b)

                    if j == 0:
                        Clock_Bias = float(split[1])
                        Clock_drift = float(split[2])
                        tk = float(split[3])
                       
                    elif j == 1:
                        X = (split[0])
                        X_dot = float(split[1])
                        X_dotdot = float(split[2])
                        SV_health = float(split[3])
                       
                    elif j == 2:
                        Y = (split[0])
                        Y_dot = float(split[1])
                        Y_dotdot = float(split[2])
                        freq_channel = float(split[3])
                       

                    elif j == 3:
                        Z = (split[0])
                        Z_dot = float(split[1])
                        Z_dotdot = float(split[2])
                        age_of_operation = float(split[3])
                    j += 1
                   
        
                GLONASS.append({
                    "system": "GLONASS",
                    "sat": satellitename,
                    "epoch": yearmonthdate,
                    "UTC_time": UTC_clock,
                    "Clock_Bias": Clock_Bias,
                    "Clock_drift": Clock_drift,
                    "tk": tk,
                    "X": X,
                    "X_speed": X_dot,
                    "X_acceleration": X_dotdot,
                    "SV_health": SV_health,
                    "Y": Y,
                    "Y_speed": Y_dot,
                    "Y_acceleration": Y_dotdot,
                    "freq_channel k": freq_channel,
                    "Z": Z,
                    "Z_speed": Z_dot,
                    "Z_acceleration": Z_dotdot,
                    "age_of_operation": age_of_operation
                })
                    
                i +=4
            
            elif line.startswith("E"):
                block = lines[i:i+8]

                j = 0
                for b in block:
                    split = split_rinex_line(b)

                    if j == 1:
                        Crs = float(split[1])
                        Delta_N = float(split[2])
                        M0 = float(split[3])

                    elif j == 2:
                        Cuc= (split[0])
                        e = float(split[1])
                        Cus = float(split[2])
                        a_sqrt = float(split[3])

                    elif j == 3:
                        toe = (split[0])
                        Cic = float(split[1])
                        lambda0 = float(split[2])
                        Cis = float(split[3])

                    elif j == 4:
                        i0 = (split[0])
                        Crc = float(split[1])
                        omega = float(split[2])
                        OMEGA_dot = float(split[3])
      
                    elif j == 5:
                        i_dotdot = (split[0])
            
                    
                    j += 1

                Galileo.append({
                    "system": "Galileo",
                    "sat": satellitename,
                    "epoch": yearmonthdate,
                    "UTC_time": UTC_clock,
                    "Crs": Crs,
                    "Delta_N": Delta_N,
                    "Cuc": Cuc,
                    "M0": M0,
                    "Cus": Cus,
                    "e": e,
                    "a_sqrt": a_sqrt,
                    "toe": toe,
                    "Cic": Cic,
                    "lambda0": lambda0,
                    "Cis": Cis,
                    "i0": i0,
                    "Crc": Crc,
                    "omega": omega,
                    "OMEGA_dot": OMEGA_dot,
                    "i_dotdot": i_dotdot
                  
                })
                
                i +=8

            
            elif line.startswith("C"):
                block = lines[i:i+8]

                j=0
                for b in block:
                    split = split_rinex_line(b)
                    if j == 1:
                        Crs = float(split[1])
                        Delta_N = float(split[2])
                        M0 = float(split[3])

                 
                    elif j == 2:
                        Cuc = (split[0])
                        e = float(split[1])
                        Cus = float(split[2])
                        a_sqrt = float(split[3])
          
                    elif j == 3:
                        toe = (split[0])
                        Cic = float(split[1])
                        lambda0 = float(split[2])
                        Cis = float(split[3])
              

                    elif j == 4:
                        i0 = (split[0])
                        Crc = float(split[1])
                        omega = float(split[2])
                        OMEGA_dot = float(split[3])
             

                    elif j == 5:
                        i_dotdot = (split[0])
    
                    j += 1
                
                BeiDou.append({
                    "system": "BeiDou",
                    "sat": satellitename,
                    "epoch": yearmonthdate,
                    "UTC_time": UTC_clock,
                    "Crs": Crs,
                    "Delta_N": Delta_N,
                    "Cuc": Cuc,
                    "M0": M0,
                    "Cus": Cus,
                    "e": e,
                    "a_sqrt": a_sqrt,
                    "toe": toe,
                    "Cic": Cic,
                    "lambda0": lambda0,
                    "Cis": Cis,
                    "i0": i0,
                    "Crc": Crc,
                    "omega": omega,
                    "OMEGA_dot": OMEGA_dot,
                    "i_dotdot": i_dotdot
                })
                i +=8
        

            elif line.startswith("J") or line.startswith("I"):
                i +=8

            
            elif line.startswith("S"):
                i +=4

            else: return "Error in reading"
     
    GPSDf = pd.DataFrame(GPS) 
    GalileoDf = pd.DataFrame(Galileo)
    BeiDouDf = pd.DataFrame(BeiDou)
    GLONASSDf = pd.DataFrame(GLONASS)
    
    return GPSDf, GalileoDf, BeiDouDf



def split_rinex_line(line):
    return [line[i:i+19].strip() for i in range(4, len(line), 19) if line[i:i+19].strip()]
