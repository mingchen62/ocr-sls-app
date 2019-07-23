import pytesseract
import PIL.Image
import io
import os
import json
from base64 import b64decode
import boto3
import logging
import hashlib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

LAMBDA_TASK_ROOT = os.environ.get('LAMBDA_TASK_ROOT', os.path.dirname(os.path.abspath(__file__)))
print("LAMBDA_TASK_ROOT ", LAMBDA_TASK_ROOT)
os.environ["PATH"] += os.pathsep + LAMBDA_TASK_ROOT

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
table = dynamodb.Table('ocr_cache')

def get_from_cache(md5_hash):
    try:
        response = table.get_item(
            Key={
                "md5_hash": md5_hash
            },
            ProjectionExpression="reco"
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return None
    else:
        if 'Item' in response:
            item = response['Item']
            logger.info("GetItem succeeded:")
            logger.info(json.dumps(item, indent=4))
            return item
        else:
            logger.info("Not found")
            return None


def put_to_cache(md5_hash, ocr_result):
    try:
        response = table.put_item(
            Item={
                'md5_hash': md5_hash,
                'reco': ocr_result
            }
        )

        logger.info("PutItem succeeded:")
    except:
        logger.error("PutItem error")

def generate_file_md5(filename, blocksize=2**20):
    m = hashlib.md5()
    with open( filename, "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()


def lambda_handler(event, context):
  #print("Event Passed to Handler: " + json.dumps(event))

  # image decoding
  try:
    image_base64 = json.loads(event['body'])['image64']
    binary = b64decode(image_base64)
  except Exception as error:
    logger.exception(error)
    return {
      'statusCode': 400,
      'headers': {'Content-Type': 'application/json'},
      'body': json.dumps({'reco': "image data error"})
    }

  # write to  request body data into file first in case a big image
  md5_hash= ""
  image= None
  try:
    m = hashlib.md5()
    image = PIL.Image.open(io.BytesIO(binary))
    with io.BytesIO() as memf:
      image.save(memf, 'PNG')
      data = memf.getvalue()
      m.update(data)
      md5_hash=m.hexdigest()
      print("md5_hash", str(md5_hash))
  except:
    return {
      'statusCode': 500,
      'headers': {"content-type": "application/json"},
      'body': "server internal  error"
    }
    # try cache
  try:
    cache_res = get_from_cache(md5_hash)
  except:
    cache_res = None

  if cache_res is not None:
    return {
      'statusCode': 200,
      'headers': {"content-type": "application/json"},
      'body': json.dumps(cache_res)
    }
  # image recognition
  try:
    res = pytesseract.image_to_string(image, config='--psm 6')
    put_to_cache(md5_hash, res)
  except  Exception as error:
    logger.exception(error)
    return {
      'statusCode': 500,
      'headers': {'Content-Type': 'application/json'},
      'body': json.dumps({'reco': "Server internal error"})
    }
  # completed and return   
  return {
      'statusCode': 200,
      'headers': {'Content-Type': 'application/json'},
      'body': json.dumps({'reco': res})
  }