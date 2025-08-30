import json
from bottle import Bottle, run, request, response, HTTPError

from speech_to_text import SpeechToText
from site_manager import SiteManager

app = Bottle()
plugins_dict = {
    "plugins": [
        "speech-to-text",
        "website-builder"
    ]
}

stt = SpeechToText()
site_manager = SiteManager()

# CORS headers for local frontend integration only
def enable_cors():
    origin = request.get_header('Origin')
    # Only allow requests from localhost/127.0.0.1
    allowed_origins = [
        'http://localhost:3000', 'http://localhost:4321', 'http://localhost:5173',
        'http://127.0.0.1:3000', 'http://127.0.0.1:4321', 'http://127.0.0.1:5173',
        'http://localhost:8080', 'http://127.0.0.1:8080'
    ]
    
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

@app.hook('before_request')
def restrict_to_localhost():
    # Get client IP address (check multiple sources for robustness)
    client_ip = (
        request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
        request.environ.get('HTTP_X_REAL_IP', '').strip() or  
        request.environ.get('REMOTE_ADDR', '')
    )
    
    # Comprehensive localhost checking
    localhost_patterns = [
        '127.0.0.1', '::1', 'localhost',
        '0.0.0.0',  # Sometimes shows up in development
    ]
    
    # Check if IP starts with 127. (entire 127.x.x.x range)
    is_loopback = client_ip.startswith('127.') or client_ip in localhost_patterns
    
    if not is_loopback:
        raise HTTPError(403, f"Access denied: API restricted to localhost only (attempted from {client_ip})")

@app.hook('after_request')
def after_request():
    enable_cors()

@app.route('/api/v1/<path:path>', method='OPTIONS')
def handle_options(path):
    enable_cors()

@app.get("/api/v1/plugins")
def plugins():
    return plugins_dict

# STT Endpoints
@app.get("/api/v1/plugins/stt/recording/start")
def audio_recording_start():
    stt.start_recording()
    return {"status": "recording_started"}

@app.get("/api/v1/plugins/stt/recording/stop")
def audio_recording_stop():
    text = stt.stop_recording()
    return {"transcription": text}

# Site Management Endpoints
@app.get("/api/v1/sites")
def list_sites():
    return {"sites": site_manager.list_sites()}

@app.post("/api/v1/sites")
def create_site():
    data = request.json or {}
    name = data.get("name")
    description = data.get("description", "")
    
    if not name:
        raise HTTPError(400, "Site name is required")
    
    site = site_manager.create_site(name, description)
    return {"site": site}

@app.get("/api/v1/sites/<site_id>")
def get_site(site_id):
    site = site_manager.get_site(site_id)
    if not site:
        raise HTTPError(404, "Site not found")
    return {"site": site}

@app.put("/api/v1/sites/<site_id>")
def update_site(site_id):
    data = request.json or {}
    name = data.get("name")
    description = data.get("description")
    
    site = site_manager.update_site(site_id, name, description)
    if not site:
        raise HTTPError(404, "Site not found")
    return {"site": site}

@app.delete("/api/v1/sites/<site_id>")
def delete_site(site_id):
    success = site_manager.delete_site(site_id)
    if not success:
        raise HTTPError(404, "Site not found")
    return {"deleted": True}

# Page Management Endpoints
@app.get("/api/v1/sites/<site_id>/pages")
def list_pages(site_id):
    pages = site_manager.list_pages(site_id)
    return {"pages": pages}

@app.get("/api/v1/sites/<site_id>/pages/<page_id>")
def get_page(site_id, page_id):
    content = site_manager.get_page_content(site_id, page_id)
    if content is None:
        raise HTTPError(404, "Page not found")
    return {"content": content}

@app.post("/api/v1/sites/<site_id>/pages")
def create_page(site_id):
    data = request.json or {}
    page_id = data.get("name")  # Changed from "page_id" to "name"
    template = data.get("template", "")
    
    if not page_id:
        raise HTTPError(400, "Page name is required")
    
    success = site_manager.create_page(site_id, page_id, template)
    if not success:
        raise HTTPError(400, "Failed to create page or site not found")
    
    return {"page_id": page_id, "created": True}

@app.put("/api/v1/sites/<site_id>/pages/<page_id>")
def update_page(site_id, page_id):
    data = request.json or {}
    content = data.get("content", "")
    
    success = site_manager.update_page_content(site_id, page_id, content)
    if not success:
        raise HTTPError(404, "Page or site not found")
    
    return {"updated": True}

@app.delete("/api/v1/sites/<site_id>/pages/<page_id>")
def delete_page(site_id, page_id):
    success = site_manager.delete_page(site_id, page_id)
    if not success:
        raise HTTPError(400, "Cannot delete page (not found or is index page)")
    
    return {"deleted": True}

if __name__ == "__main__":
    # Listen only on localhost (127.0.0.1)
    run(app, host="127.0.0.1", port=8000, debug=True)

