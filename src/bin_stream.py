import argparse
from ctypes import sizeof
import profile
from typing import List
from IsoData import IsoFrameInfo, IsoVertex
from IsoData import IsoTriangle, IsoVertAndTri
import struct
import sys, threading
import json
import os
import gzip
# from memory_profiler import profile

FILE_PATH = "./static/upload/"
HEAD_OFFSET = 28
DATA_OFFSET = 4
INT32_SIZE = 4
FLOAT_SIZE = 4

# level count = 10
# temp count = 0
# vert count = 

# m_fileStream = open("".join([FILE_PATH,"FDS_evac_ch4-150_20190502_02.iso"]),mode='rb')

# @profile
def read_info_iso_and_save_json(file_name,target_level):
    try:
        with open("".join([FILE_PATH,file_name,".iso"]),mode='rb') as f:
            frames = []
            vts = []
            headerSize = 0

            # header offset
            headerSize += HEAD_OFFSET   #28
            f.read(HEAD_OFFSET)

            ### levels
            # levelCount = f.read(INT32_SIZE)
            # levelCount = int(f.read(INT32_SIZE),16);
            
            levelCount = int.from_bytes(f.read(INT32_SIZE), byteorder='little');
            headerSize += DATA_OFFSET;
            f.read(DATA_OFFSET)

            # print("level count",levelCount)
            levels = [0 for _ in range(levelCount)];

            if 0 < levelCount:
                headerSize += DATA_OFFSET;
                f.read(DATA_OFFSET)

                for i in range(0,levelCount):
                    # TODO: float bytes으로 바꾸기
                    # levels[i] = int.from_bytes(f.read(INT32_SIZE), byteorder='little');
                    levels[i] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                    headerSize += DATA_OFFSET;

                headerSize += DATA_OFFSET;
                f.read(DATA_OFFSET)

            headerSize += DATA_OFFSET;
            f.read(DATA_OFFSET)
            # print(levels)
            

            ### Temp
            tempCount:int = int.from_bytes(f.read(INT32_SIZE), byteorder='little')
            headerSize += 4;
            headerSize += DATA_OFFSET;
            f.read(DATA_OFFSET)

            # print("tempCount",tempCount)
            if tempCount > 0:
                headerSize += DATA_OFFSET;
                f.read(DATA_OFFSET)

                for i in range(1,tempCount):
                    headerSize += DATA_OFFSET;
                    f.read(DATA_OFFSET)
                headerSize += DATA_OFFSET;
                f.read(DATA_OFFSET)
            #### END Temp


            while f.readable:
                try:
                    info = IsoFrameInfo();

                    if len(frames) == 0:
                        info.byte_size += headerSize;

                    # Time
                    localTimes = [0,0];
                    info.byte_size += 4;
                    f.read(DATA_OFFSET)

                    localTimes[0] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                    info.byte_size += 4;
                    localTimes[1] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                    info.byte_size += 4;

                    _time_old = info.time_sec
                    info.time_sec = localTimes[0];
                    _dt =  info.time_sec - _time_old
                    # END Time

                    info.byte_size += DATA_OFFSET
                    f.read(DATA_OFFSET)

                    ###########################
                    #### Vert & Tri Count #####
                    ###########################
                    info.byte_size += DATA_OFFSET
                    f.read(DATA_OFFSET)

                    info.ver_count = int.from_bytes(f.read(INT32_SIZE), byteorder='little')
                    info.byte_size += 4;
                    # print('vert time/count :',info.time_sec,info.ver_count)

                    info.tri_count = int.from_bytes(f.read(INT32_SIZE), byteorder='little')
                    info.byte_size += 4;
                    # print('tri time/count :',info.time_sec,info.tri_count)

                    info.byte_size += DATA_OFFSET
                    f.read(DATA_OFFSET)

                    vertAndTri = IsoVertAndTri()

                    if 0 < info.ver_count and 0 < info.tri_count:
                        info.vert_start_offset = info.byte_size

                        ## Read XYZ vertices coords
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)
                        for i in range(0,info.ver_count):
                            info.byte_size += 12;
                            # f.read(12)    # offset 이동만 하는 용도
                            v = IsoVertex()
                            v.XYZ[0] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                            v.XYZ[1] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                            v.XYZ[2] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                            vertAndTri.vertices.append(v)
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)

                        ## Read XYZW[012] Triangles topologies
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)
                        for i in range(0,info.tri_count):
                            info.byte_size += 12;
                            # f.read(12)
                            t = IsoTriangle()
                            t.XYZW[0] = int.from_bytes(f.read(INT32_SIZE), byteorder='little')
                            t.XYZW[1] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
                            t.XYZW[2] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
                            vertAndTri.triangles.append(t)
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)

                        ## Read XYZW[3] Levels
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)
                        for i in range(0,info.tri_count):
                            info.byte_size += DATA_OFFSET
                            # f.read(DATA_OFFSET)
                            vertAndTri.triangles[i].XYZW[3] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
                        info.byte_size += DATA_OFFSET
                        f.read(DATA_OFFSET)

                    if info.ver_count == 0 and info.tri_count == 0:
                        if (len(frames) == 0):
                            info.byte_size += 16;
                            f.read(16)
                        else:
                            break;
                    ###########################
                    ###########################
                    ###########################

                    info.acc_byte_size = info.byte_size
                    if (len(frames) != 0):
                        info.acc_byte_size += frames[-1].acc_byte_size;

                    # level로 필터링된 triangles를 이루는 XYZ 좌표 행렬만 

                    tri_count_in_level = 0
                    _tri = []
                    _ver = []

                    vt = IsoVertAndTri()
                    vt.time_sec = info.time_sec
                    vt.cur_frame = len(frames)

                    for i in range(info.tri_count):
                        t = vertAndTri.triangles[i]
                        if target_level == -1 or t.XYZW[3] == target_level +1:
                            tri_count_in_level += 1
                            vt.triangles.append(t)
                            # _tri.append(t.XYZW[0]-1)
                            # _tri.append(t.XYZW[2]-1)
                            # _tri.append(t.XYZW[1]-1)

                    if tri_count_in_level != 0:
                        vt.vertices = vertAndTri.vertices
                        # for i in range(info.ver_count):
                        #     v = vertAndTri.vertices[i]
                            # _ver.append([v.XYZ[0],v.XYZ[2],v.XYZ[1]])

                    
                    frames.append(info)
                    n_frames = len(frames)-1
                    vts.append(vt)

                    ## next_time & total frame 제대로 입력이 안됨
                    ## next_time -> DT 로 바꾸기?!
                    # json_save_path = f'static/jsons/{file_name}/vt_{file_name}_{n_frames}.json'
                    # os.makedirs(os.path.dirname(json_save_path), exist_ok=True)
                    # with open(json_save_path, 'w') as f1:
                    #     vt.total_frame = len(frames)
                    #     vt.dt = _dt
                    #     json.dump(vt.serialize(),f1)

                    

                    json_save_path = f'static/jsons/{file_name}/vt_{file_name}_{n_frames}.json'
                    os.makedirs(os.path.dirname(json_save_path), exist_ok=True)
                    with gzip.open(json_save_path + '.gz', 'wb') as f1:
                        vt.total_frame = len(frames)
                        vt.dt = _dt
                        serialized_data = vt.serialize()
                        f1.write(json.dumps(serialized_data).encode('utf-8'))

                    
                    print(f'frame:{len(frames)},t:{info.time_sec:.2f}, level:{target_level}, vert: {len(vt.vertices)}, tri: {len(vt.triangles)}')
                except Exception as e:
                    print(e)
                    # for info in frames:
                        # print(len(frames), info.time_sec, info.byte_size)
                    break

                # curr_position = f.tell()
                # total_len = len(f)
                # print('cur_pos/total',curr_position,total_len)
                # if curr_position > total_len:
                #     break;

            ## save as json
        
        ## TODO:OBJ 3D format to Mesh Simplification

        return frames, vts

    except IOError:
        print('Error While Opening the file!')  

def read_geo_iso_step(n,file_name,acc_byte_size,info,target_level):
    try:
        with open("".join([FILE_PATH,file_name]),mode='rb') as f:
            f.read(acc_byte_size)
            f.read(info.vert_start_offset)

            vertAndTri = IsoVertAndTri();

            ## Vert
            f.read(4);
            for i in range(0,info.ver_count):
                v = IsoVertex()
                v.XYZ[0] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                v.XYZ[1] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                v.XYZ[2] = struct.unpack('f', f.read(FLOAT_SIZE))[0]
                vertAndTri.vertices.append(v)
            f.read(4);

            ## Tri
            f.read(4);
            for i in range(0,info.tri_count):
                t = IsoTriangle()
                t.XYZW[0] = int.from_bytes(f.read(INT32_SIZE), byteorder='little')
                t.XYZW[1] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
                t.XYZW[2] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
                vertAndTri.triangles.append(t)
            f.read(4);

            ## Level
            f.read(4);
            for i in range(0,info.tri_count):
                vertAndTri.triangles[i].XYZW[3] = int.from_bytes(f.read(INT32_SIZE), byteorder='little') 
            f.read(4);

            # if target_frame == 0 and info.ver_count == 0 and info.tri_count == 0:
                # f.read(16);


            print(f'frame:{n}, level:, vert: {info.ver_count}, tri: {info.tri_count}')
            return vertAndTri

    except IOError:
        print('Error While Opening the file!')  
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Specify target ISO to process from *.iso to *.json or *.json.gz")
    parser.add_argument("target_iso", help=": input iso file name")

    args = parser.parse_args()

    target_iso = args.target_iso
    
    target_level = 0
    frames, unity = read_info_iso_and_save_json(target_iso,target_level)
    

    # for i in range(len(frames)):
    #     # TODO: vert count 가 0이면 그냥 tri는 pass 해도 됨.
    #     if i == 0:
    #         acc_byte_size = 0
    #         read_geo_iso_step(i,target_iso,acc_byte_size,frames[i])
    #     else:
    #         read_geo_iso_step(i,target_iso,frames[i-1].acc_byte_size,frames[i])
