import os
from flask_cors import CORS
from flask import Flask, request, abort, jsonify, send_from_directory
from bin_stream import *
from flask import Response

import time
import logging
import threading
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


api = Flask(__name__)

ALLOWED_EXTENSIONS = {'iso'}

MAX_CONTENT_LENGTH = 4 * 1024 * 1024 * 1024 # Limit file size to 4G
UPLOAD_DIRECTORY = "static/upload"
JSON_DIRECTORY = "static/jsons"
OBJ_DIRECTORY = "static/objs"


if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
api.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY

queue = Queue()

# Define the function to be executed when a new file is added
def on_created(event):
    if not event.is_directory and event.src_path.endswith('.iso'):
        iso_path = event.src_path
        is_upload_complete = False
        print(f"New iso file uploading...: {iso_path}")
        while not is_upload_complete:
            initial_size = os.path.getsize(iso_path)
            time.sleep(1)
            current_size = os.path.getsize(iso_path)
            if current_size == initial_size:
                is_upload_complete = True
        target_iso, _ = event.src_path.split('/')[-1].split('.')
        print(f"New iso file detected : {target_iso}")
        thread = threading.Thread(target=read_info_iso_and_save_json, args=(target_iso, 0))
        thread.start()


# Define the watchdog event handler
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        on_created(event)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/iso/upload', methods=['POST'])
def upload_iso():
    """
    Upload a file to the server.

    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .iso files are allowed.'}), 400
    
    # Save the file to the upload directory
    file_path = os.path.join(api.config['UPLOAD_DIRECTORY'], file.filename)
    file.save(file_path)
    
    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

@api.route("/iso/list", methods=['GET'])
def list_iso():
    """
    List all files on the server.

    """
    files = [os.path.join(api.config['UPLOAD_DIRECTORY'], f) for f in os.listdir(api.config['UPLOAD_DIRECTORY']) if os.path.isfile(os.path.join(api.config['UPLOAD_DIRECTORY'], f))]
    if not files:
        return jsonify({'error': 'No files found on the server.'}), 404
    return jsonify(files), 200



@api.route("/iso/download/<iso_filename>", methods=['GET'])
def download_iso(iso_filename):
    """
    Download a file from the server.
    """
    file_path = os.path.join(api.config['UPLOAD_DIRECTORY'], iso_filename)
    if not os.path.isfile(file_path):
        return jsonify({'error': 'The requested file could not be found.'}), 404
    return send_from_directory(api.config['UPLOAD_DIRECTORY'], iso_filename, as_attachment=True)


@api.route("/iso/stream/<iso_filename>")
def read_iso(iso_filename:str):
    # target_iso = "FDS_evac_ch4-150_20190502_02"
    # target_level = 0
    target_value = request.args['target_value']
    cur_frame = request.args['req_frame']
    # total_frame = request.args['total']

    target_file_name = f'{JSON_DIRECTORY}/{iso_filename}/vt_{iso_filename}_{cur_frame}.json'
    jvt = None
    if not os.path.exists(target_file_name+'.gz'):
        print("target json file not exist, iso processing started : ")
        
        # return jsonify([f.serialize() for f in frames])
        # with open(f'{iso_filename}.json', 'w') as f:
        #     json.dump(jvt, f)
    # else:
    if os.path.exists(target_file_name+'.gz'):
        with open(target_file_name+'.gz', 'rb') as f:
            # Read the file content
            jvt_gz = f.read()
            # print("target json file exist, Reponse start : ")

            response = Response(jvt_gz, content_type='application/gzip', headers={'Content-Encoding': 'gzip'})
        return response

if __name__ == "__main__":
    # Define the watchdog observer and start monitoring the directory
    observer = Observer()
    observer.schedule(NewFileHandler(), path='static/upload',recursive=True)
    observer.start()
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='iso-stream.log',
                    filemode='a')
    logger = logging.getLogger()

    CORS(api, resources={r"/iso/*": {"origins": "*"}})

    api.run(debug=True,host="0.0.0.0", port=5000)

