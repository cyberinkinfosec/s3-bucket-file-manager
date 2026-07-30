#!/usr/bin/env python3

from flask import (
    Flask,
    request,
    redirect,
    render_template_string,
    send_file
)

import boto3
import os
import io
import mimetypes
from datetime import datetime


app = Flask(__name__)


# =====================================
# AWS CONFIGURATION
# =====================================

AWS_REGION = "us-east-1"


# Add all your buckets here

S3_BUCKETS = [

    "Bucket1",
    "Bucket2"
]

AWS_ACCESS_KEY =""
AWS_SECRET_KEY =""



s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)



# =====================================
# HTML
# =====================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<title>
S3 Multi Bucket Manager
</title>


<style>

body {

font-family:Arial;
background:#eeeeee;
padding:30px;

}


.container {

background:white;
padding:25px;
border-radius:12px;

}


table {

width:100%;
border-collapse:collapse;
margin-top:20px;

}


th {

background:#222;
color:white;

}


td,th {

padding:10px;
border-bottom:1px solid #ddd;

}


a {

text-decoration:none;

}


.folder {

color:#d27b00;
font-weight:bold;

}


button,input {

padding:8px;

}


</style>


</head>


<body>


<div class="container">


<h2>
☁ Multi S3 File Manager
</h2>


{% if not bucket %}


<h3>
Buckets
</h3>


{% endif %}



<form>


<input
type="hidden"
name="bucket"
value="{{bucket}}">


<input
type="hidden"
name="prefix"
value="{{prefix}}">


<input
name="search"
placeholder="Search files"
value="{{search}}">


From:

<input
type="date"
name="from_date"
value="{{from_date}}">


To:

<input
type="date"
name="to_date"
value="{{to_date}}">


<button>
Search
</button>


</form>



<br>


{% if bucket %}

<form
method="post"
action="/upload"
enctype="multipart/form-data">


<input
type="hidden"
name="bucket"
value="{{bucket}}">


<input
type="hidden"
name="prefix"
value="{{prefix}}">


<input
type="file"
name="file">


<button>
Upload
</button>


</form>


<br>


Bucket:

<b>{{bucket}}</b>


<br>


Path:

<b>{{prefix}}</b>


<br>


<a href="/">
⬅ Buckets
</a>


{% endif %}




<table>


<tr>

<th>Name</th>

<th>Size</th>

<th>Date</th>

<th>Action</th>

</tr>



{% for f in files %}


<tr>


<td>


{% if f.folder %}


📁


<a class="folder"
href="/?bucket={{f.bucket}}&prefix={{f.key}}">


{{f.name}}


</a>


{% else %}


📄 {{f.name}}


{% endif %}


</td>



<td>

{{f.size}}

</td>



<td>

{{f.date}}

</td>



<td>


{% if not f.folder %}


<a href="/preview?bucket={{f.bucket}}&key={{f.key}}">
Preview
</a>

|

<a href="/download?bucket={{f.bucket}}&key={{f.key}}">
Download
</a>


|

<a href="/delete?bucket={{f.bucket}}&key={{f.key}}">
Delete
</a>


{% endif %}


</td>


</tr>


{% endfor %}



</table>


</div>


</body>

</html>

"""





# =====================================
# MAIN BROWSER
# =====================================


@app.route("/")
def index():


    bucket = request.args.get(
        "bucket",
        ""
    )


    prefix = request.args.get(
        "prefix",
        ""
    )


    search=request.args.get(
        "search",
        ""
    )


    from_date=request.args.get(
        "from_date",
        ""
    )


    to_date=request.args.get(
        "to_date",
        ""
    )



    files=[]



    # SHOW BUCKETS

    if not bucket:


        for b in S3_BUCKETS:


            files.append({

                "folder":True,

                "bucket":b,

                "key":"",

                "name":b,

                "size":"",

                "date":""

            })



        return render_template_string(

            HTML,

            files=files,

            bucket="",

            prefix="",

            search=search,

            from_date=from_date,

            to_date=to_date

        )





    # LIST BUCKET


    result=s3.list_objects_v2(

        Bucket=bucket,

        Prefix=prefix,

        Delimiter="/"

    )




    # FOLDERS

    for item in result.get(
        "CommonPrefixes",
        []
    ):


        key=item["Prefix"]


        files.append({

            "folder":True,

            "bucket":bucket,

            "key":key,

            "name":
            key.rstrip("/").split("/")[-1],

            "size":"",

            "date":""

        })




    # FILES

    for obj in result.get(
        "Contents",
        []
    ):


        key=obj["Key"]


        if key == prefix:
            continue



        name=key.split("/")[-1]


        modified=obj["LastModified"]




        if search:

            if search.lower() not in name.lower():

                continue




        if from_date:


            start=datetime.strptime(
                from_date,
                "%Y-%m-%d"
            )


            if modified.replace(
                tzinfo=None
            ) < start:

                continue




        if to_date:


            end=datetime.strptime(
                to_date,
                "%Y-%m-%d"
            )


            if modified.replace(
                tzinfo=None
            ) > end:

                continue





        files.append({

            "folder":False,

            "bucket":bucket,

            "key":key,

            "name":name,

            "size":
            obj["Size"],

            "date":
            modified.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        })





    return render_template_string(

        HTML,

        files=files,

        bucket=bucket,

        prefix=prefix,

        search=search,

        from_date=from_date,

        to_date=to_date

    )






# =====================================
# UPLOAD
# =====================================
@app.route("/preview")
def preview():

    bucket = request.args["bucket"]
    key = request.args["key"]

    filename = os.path.basename(key)

    obj = s3.get_object(
        Bucket=bucket,
        Key=key
    )


    file_data = obj["Body"].read()


    mime_type, _ = mimetypes.guess_type(filename)


    if not mime_type:
        mime_type = "application/octet-stream"


    response = send_file(

        io.BytesIO(file_data),

        mimetype=mime_type,

        download_name=filename,

        as_attachment=False

    )


    # Force browser preview
    response.headers["Content-Disposition"] = (
        f'inline; filename="{filename}"'
    )


    return response

@app.route(
"/upload",
methods=["POST"]
)

def upload():


    bucket=request.form["bucket"]

    prefix=request.form["prefix"]

    file=request.files["file"]


    key=prefix + file.filename



    s3.upload_fileobj(

        file,

        bucket,

        key

    )


    return redirect(

        f"/?bucket={bucket}&prefix={prefix}"

    )






# =====================================
# DOWNLOAD
# =====================================


@app.route("/download")
def download():

    bucket = request.args.get("bucket")
    key = request.args.get("key")

    try:
        obj = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        data = obj["Body"].read()

        filename = os.path.basename(key)

        mime_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if filename.lower().endswith(".xlsx")
            else "application/octet-stream"
        )

        return send_file(
            io.BytesIO(data),
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return f"Download failed: {e}", 500


# =====================================
# DELETE
# =====================================


@app.route("/delete")

def delete():


    bucket=request.args["bucket"]

    key=request.args["key"]



    s3.delete_object(

        Bucket=bucket,

        Key=key

    )


    return redirect(

        f"/?bucket={bucket}"

    )







# =====================================
# START
# =====================================


if __name__=="__main__":


    print()
    print("==============================")
    print(" Multi S3 File Manager")
    print("==============================")
    print()
    print(
        "Open http://127.0.0.1:5000"
    )
    print()



    app.run(

        host="127.0.0.1",

        port=5000

    )
