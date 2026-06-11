# Project



## Getting started

Before you can run the code on your local computer, you need to download the terrain data and the ephemerides from CDDIS. 

The application is found here: 
[https://master-2025.vercel.app](https://tina-master-2026.vercel.app/)
## Add your files


```
cd existing_repo
git remote add origin https://gitlab.stud.idi.ntnu.no/tinalhe/project.git
git branch -M main
git push -uf origin main
```


## Terrain data
The terrain data I used in the project is added as a zip.file in the attachment folder on Inspera. This has to be unzipped and placed under the "data" folder in the Backend folder.



## Broadcast ephemerides

The broadcast ephemerides can be downloaded from [https://cddis.nasa.gov/archive/gnss/data/daily/2025/brdc](https://cddis.nasa.gov/archive/gnss/data/daily/2025/brdc) 
This step is a bit tricky, because a .netrc-file has to be created in advance.

1. Create an Earthdata-user here [https://urs.earthdata.nasa.gov/users/new](https://urs.earthdata.nasa.gov/users/new) 
2. Set up a .netrc-file:
   - Placement
     - Mac/Linux: ~/.netrc
     - Windows (WSL/git bash): C:\Users\YourUsername\.netrc or use WSL's ~/.netrc
   - Replace username and password with your Earthdata user

      machine urs.earthdata.nasa.gov
      login username
      password password

## Start project

- Start a terminal
- Nagivate to the backend folder:

   cd backend
   pip install -r requirements.txt
    python app.py

- Navigate to the frontend folder
- start a new terminal


  cd frontend
  npm install
  mpm start


