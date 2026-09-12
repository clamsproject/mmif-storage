# Script that runs a bunch of commands.
#
# Assumes that the jq utility is installed.
# Assumes an API running on port 8000 and the MMIF data in data/storage-example.


echo '\n>>> ANALYTICS\n'
curl --silent 'http://127.0.0.1:8000/analytics' -H 'accept: application/json' |jq

read
echo '\n\n>>> PATHS\n'
curl --silent 'http://127.0.0.1:8000/paths' -H 'accept: application/json' | jq

read
echo '\n\n>>> PEEK\n'
curl --silent -X POST 'http://127.0.0.1:8000/peek' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "workflow": [
    { "app": "swt-detection", "version": "v8.6", "properties": {} },
    { "app": "smolvlm2-captioner", "version": "v1.0", "properties": {} } ]
}' | jq

read
echo '\n\n>>> UPLOAD\n'
curl --silent -X POST 'http://127.0.0.1:8000/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data/cpb-aacip-f551104e446-clip1.mmif' | jq

read
echo '\n\n>>> DOWNLOAD FILE - USING WORKFLOW\n'
curl --silent -X POST 'http://127.0.0.1:8000/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-f551104e446-clip1",
        "workflow": {"swt-detection/v8.6": {}}}' | wc

read
echo '\n\n>>> DOWNLOAD FILE - USING WORKFLOW_ID\n'
curl --silent -X POST 'http://127.0.0.1:8000/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"guid": "cpb-aacip-f551104e446-clip1",
       "workflow_id": "swt-detection/v8.6/d41d8cd98f00b204e9800998ecf8427e"}' | wc

read
echo '\n\n>>> DOWNLOAD FILE - FAILURE\n'
curl --silent -X POST 'http://127.0.0.1:8000/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ "guid": "cpb-aacip-f551104e446-clip1",
        "workflow": {"swt-detection/v8.6": {"Pretty": "True"}}}' | jq

read
echo '\n\n>>> DOWNLOAD FILES\n'
curl --silent -X POST 'http://127.0.0.1:8000/download' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  --output storage-response.zip \
  -d '{ "guid": ["cpb-aacip-f551104e446-clip1"],
        "workflow": {"swt-detection/v8.6": {}}}' | jq
ls -al *zip

echo '\n'

