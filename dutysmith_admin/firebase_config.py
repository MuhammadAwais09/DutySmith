import os
import requests

class FirebaseREST:
    def __init__(self):
        self.database_url = "https://dutysmith-25ccb-default-rtdb.firebaseio.com"
        self.api_key = os.environ.get('FIREBASE_API_KEY', 'AIzaSyDdRS9eN2K6Hq39RS6eoYnyUWqkjseQwzY')
    
    def get(self, path):
        """GET data from Firebase RTDB"""
        url = f"{self.database_url}/{path}.json"
        response = requests.get(url)
        return response.json()
    
    def put(self, path, data):
        """PUT data to Firebase RTDB"""
        url = f"{self.database_url}/{path}.json"
        response = requests.put(url, json=data)
        return response.json()
    
    def post(self, path, data):
        """POST (push) data to Firebase RTDB"""
        url = f"{self.database_url}/{path}.json"
        response = requests.post(url, json=data)
        return response.json()
    
    def patch(self, path, data):
        """PATCH (update) data in Firebase RTDB"""
        url = f"{self.database_url}/{path}.json"
        response = requests.patch(url, json=data)
        return response.json()
    
    def delete(self, path):
        """DELETE data from Firebase RTDB"""
        url = f"{self.database_url}/{path}.json"
        response = requests.delete(url)
        return response.json()

# Initialize
firebase_db = FirebaseREST()