
import numpy as np


def designMatrixA(dictionary):

    # dict = {}

    for point, systems in dictionary.items():

        x_r, y_r, z_r = point

        satellites = sum(systems.values(), [])
        satellites_len = len(satellites)
        
        if satellites_len < 4:
            print("For få satellitter")
            continue


        A = np.zeros((satellites_len, 4))
        A[:, 3] = -1

        for i, sat in enumerate(satellites):

            _, x_s, y_s, z_s, *_ = sat

            dx =  x_s - x_r
            dy =  y_s - y_r
            dz =  z_s - z_r

            r_vector = np.sqrt(dx**2+dy**2+dz**2)

            A[i, :3] = [-dx/r_vector, -dy/r_vector, -dz/r_vector]
        

        Q = np.linalg.inv(np.matmul(np.transpose(A), A))

        PDOP = np.sqrt(Q[0][0]+Q[1][1]+Q[2][2])

        print(PDOP)

    return 0




