from flask import Flask, request, render_template, redirect, url_for
import boto3

# define the needed credentials and bucket name
AWS_ACCESS_KEY_ID = "AKIAT222LRWOLK7L5N5T"
AWS_SECRET_ACCESS_KEY = "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"
BUCKET_NAME = 'danonephotobooth'
DYNAMODB_TABLE_NAME = 'Danone'

app = Flask(__name__, template_folder='/home/ec2-user/Danone')

# establish the client connection to the the S3 service of AWS
s3 = boto3.client(
    service_name="s3",
    region_name="eu-west-3",
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
        
        # Vérification de l'existence du fichier dans S3
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=f'{id}.jpg')
            image_url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': f'{id}.jpg'}, ExpiresIn=3600)
        except s3.exceptions.ClientError:
            image_url = None
        
        return render_template('result.html', nom=nom, prenom=prenom, role=role, email=email, image_url=image_url)
    
    return render_template('form.html', id=id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
