from werkzeug.utils import secure_filename
import secrets,os

AUDIO_FOLDER = 'base/static/notes_audio/'

def create_response(status, message, data=None,pagination_info=None, http_status_code=200, error=None):
    response = {
        "status": status,
        "message": message
    }

    if pagination_info is not None:
        response["pagination_info"] = pagination_info

    if data is not None:
        response["data"] = data

    if error is not None:
        response["error"] = error

    return response, http_status_code


ALLOWED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".aac",
    ".m4a",
    ".ogg",
    ".flac",
    ".amr",
    ".wma"
}

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_AUDIO_EXTENSIONS

def upload_audio_local(file):
    try:
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            extension = os.path.splitext(filename)[1].lower()

            x = secrets.token_hex(10)
            picture = x + extension

            image_path = os.path.join(AUDIO_FOLDER)
            file.save(os.path.join(image_path, picture))

            file_path = image_path.replace("base", "")

            return file_path, picture

        else:
            return {'status': 0, 'message': 'Invalid audio format'}, 400

    except Exception as e:
        print("errorrrrrrrrrrrrrrrrr:", str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500

def delete_audio_local(file):
    try:
        os.remove(os.path.join(AUDIO_FOLDER, file))
    except Exception as e:
        print('errorrrrrrrrrrrrrrrrr:', str(e))
        return {'status': 0, 'message': 'Something went wrong'}, 500