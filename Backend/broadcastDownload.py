import os
import subprocess
import gzip

folder = "data/rinex/"
os.makedirs(folder, exist_ok=True)

username = os.getenv("EARTHDATA_USERNAME") 
password = os.getenv("EARTHDATA_PASSWORD")

if not username or not password:
    raise RuntimeError("Missing EARTHDATA_USERNAME or EARTHDATA_PASSWORD")

netrc_path = "/tmp/.netrc"
with open(netrc_path, "w") as f: 
    f.write(f""" machine urs.earthdata.nasa.gov 
login {username}
password {password} 
""") 
    
os.chmod(netrc_path, 0o600)

def download(day, year):

    day = str(day).zfill(3)

    filename = f"BRDC00IGS_R_{year}{day}0000_01D_MN.rnx.gz"
    url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/brdc/{filename}"

    gz_path = os.path.join(folder, filename)
    rnx_path = gz_path[:-3]

    if os.path.exists(rnx_path):
        print("File exists:", rnx_path)
        return rnx_path

    subprocess.run([
        "curl",
        "--netrc-file", netrc_path,
        "-L",
        "-c", "cookies.txt",
        "-b", "cookies.txt",
        "-o", gz_path,
        url
    ], check=True)

    print("Unzipping...")

    with gzip.open(gz_path, "rb") as f_in:
        with open(rnx_path, "wb") as f_out:
            f_out.write(f_in.read())

    os.remove(gz_path)

    
    return rnx_path



