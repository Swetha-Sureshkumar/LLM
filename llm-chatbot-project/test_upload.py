import requests

# Test file upload
with open('test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:3000/api/upload-pdf', files=files)
    
print("Status Code:", response.status_code)
print("Response:", response.json())
