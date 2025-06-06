from flask import Flask, render_template, request, send_file
import os
from processor import process_video, first_frame

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        video = request.files["video_file"]
        if video:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
            video.save(video_path)
            
            # for the first frame only sending to frontend
            first_frame_path=first_frame(video_path)
            if(first_frame_path):
                return render_template("choosing_frame.html",frame_url="static/frames/firstframe.png",video_path=video_path)
            # output_excel = process_video(video_path)
            # return send_file(output_excel, as_attachment=True)    

    return render_template("index.html")

@app.route("/Image_coordinates",methods=["POST"])
def send_coordinates():
    coordinates=request.get_json()
    region_coordinates = coordinates.get("coordinates", [])
    videopath=coordinates.get("video_url")
    try:
        output_excel = process_video(videopath,region_coordinates)
        filename = os.path.basename(output_excel)
        return {"status": "success", "download_url": f"/download/{filename}"}
    except:
        return {"status": "error"}


@app.route("/download/<filename>")
def download_result(filename):
    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)