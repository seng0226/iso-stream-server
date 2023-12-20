# iso-stream-server
iso data streaming server to visualize through Unity3D. The `*.iso` file should be generated from Pyrosim.

# Quick Installation

```
git clone https://github.com/kimimgo/iso-stream-server.git
sh run_flask_app.sh
```
+ Required : docker, python3.9
+ Default port : 8081

# API list

+ {base_url}/iso/upload
+ {base_url}/iso/list
+ {base_url}/iso/download/<iso_filename>
+ {base_url}/iso/stream/<iso_filename> (unity에서만 사용가능)

## 주의사항

0. `static/json`, `static/upload` 폴더가 필수적으로 필요합니다. (`run_flask_app.sh`에서 폴더 자동 생성)
1. pyrosim iso 파일을 시간단위로 쪼개 압축된 형태로 `server-storage`에 저장하는 스탭을 거칩니다. `static/json`에 저장됩니다.(json-gzip)
2. {base_url}/iso/stream/<iso_filename> API를 호출하면 시간단위별로 `iso surface`를 하나씩 unity로 전송합니다.
3. iso는 {base_url}/iso/upload API를 통해 `static/upload` 파일에 저장되고, `app.py` 내부에 구현된 `watchdog`가 폴더 내 신규 iso파일을 인식하여 `1.`스탭을 자동 실행합니다.
    1. 따라서, iso가 최초 업로드되면 unity 에서 가시화 하기까지 시간이 걸립니다. (약 1~3분)

### 23-03-25 iso 현황
```
.
└── static
    ├── jsons
    │   ├── FDS_evac_ch4-150_20190502_02 {*.json.gz files}
    │   ├── Main10F
    │   ├── Main15F
    │   ├── Main5F
    │   ├── RND
    │   ├── RND_CFD_1F
    │   ├── RND_CFD_2F
    │   ├── RND_CFD_3F
    │   ├── RND_CFD_4F
    │   ├── RND_CFD_B1
    │   ├── Simple_1_1
    │   ├── Test_iso
    │   ├── previoustest_1_2
    │   └── untitled_1_11
    └── upload
        ├── FDS_evac_ch4-150_20190502_02.iso
        ├── Main10F.iso
        ├── Main15F.iso
        ├── Main5F.iso
        ├── RND.iso
        ├── RND_CFD_1F.iso
        ├── RND_CFD_2F.iso
        ├── RND_CFD_3F.iso
        ├── RND_CFD_4F.iso
        ├── RND_CFD_B1.iso
        ├── Simple_1_1.iso
        ├── Test_iso.iso
        ├── previoustest_1_2.iso
        └── untitled_1_11.iso

2 directories, 14 files

```
