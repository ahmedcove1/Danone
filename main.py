from flask import Flask, request, render_template, redirect, url_for
import boto3
import os

# define the needed credentials and bucket name
AWS_ACCESS_KEY_ID = "AKIAT222LRWOLK7L5N5T"
AWS_SECRET_ACCESS_KEY = "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"
BUCKET_NAME = 'lutindanone'
DYNAMODB_TABLE_NAME = 'Danone'

app = Flask(__name__, template_folder='/home/ec2-user/Danone')
#app = Flask(__name__, template_folder='/Users/ahmedbahri/Desktop/Danone')
# establish the client connection to the the S3 service of AWS
s3 = boto3.client(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# establish the client connection to the DynamoDB service of AWS
dynamodb = boto3.resource(
    'dynamodb',
    region_name="eu-west-3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route('/<id>', methods=['GET', 'POST'])
def form(id):
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        role = request.form['role']
        email = request.form['email']
        
        # Extraction du numéro de l'ID
        id_number = int(''.join(filter(str.isdigit, id)))
        
        # Enregistrement des informations dans DynamoDB
        table.put_item(
            Item={
                'ID': id_number,
                'nom': nom,
                'prenom': prenom,
                'role': role,
                'email': email
            }
        )
        
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=f'{id}.jpg')
            image_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': f'{id}.jpg'}, ExpiresIn=3600)
            print(image_url)
        except s3.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            print(e)
            if error_code == '403':
                print(f"Access denied for object {id}.jpg in bucket {BUCKET_NAME}. Check your permissions.")
            elif error_code == '404':
                print(f"Object {id}.jpg not found in bucket {BUCKET_NAME}.")
            elif error_code == 'AccessDenied':
                print(f"Explicit deny for object {id}.jpg in bucket {BUCKET_NAME}. Check your IAM policies.")
            elif error_code == '500':
                print(f"Server error for object {id}.jpg in bucket {BUCKET_NAME}. Please try again later.")
            else:
                print(f"Error occurred: {e}")
            image_url = None
        
        return render_template('result.html', nom=nom, prenom=prenom, role=role, email=email, image_url=image_url)
    
    return render_template('form.html', id=id)

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, host=host, port=port)
