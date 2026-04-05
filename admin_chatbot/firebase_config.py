# firebase_config.py
# Firebase REST API Handler

import requests
from config import Config

class FirebaseREST:
    """Firebase Realtime Database REST API Handler"""
    
    def __init__(self):
        self.database_url = Config.FIREBASE_DATABASE_URL
        self.api_key = Config.FIREBASE_API_KEY
        self.timeout = 10
    
    def _make_request(self, method, path, data=None):
        """Make HTTP request to Firebase"""
        url = f"{self.database_url}/{path}.json"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=self.timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=self.timeout)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=self.timeout)
            else:
                return None
            
            return response.json()
        except requests.exceptions.Timeout:
            print(f"Firebase {method} timeout for path: {path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Firebase {method} error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def get(self, path):
        """GET data from Firebase RTDB"""
        return self._make_request('GET', path)
    
    def put(self, path, data):
        """PUT data to Firebase RTDB (overwrite)"""
        return self._make_request('PUT', path, data)
    
    def post(self, path, data):
        """POST (push) data to Firebase RTDB"""
        return self._make_request('POST', path, data)
    
    def patch(self, path, data):
        """PATCH (update) data in Firebase RTDB"""
        return self._make_request('PATCH', path, data)
    
    def delete(self, path):
        """DELETE data from Firebase RTDB"""
        return self._make_request('DELETE', path)


# Initialize Firebase instance
firebase_db = FirebaseREST()