import urllib.parse
import re
from pathlib import Path
from bottle import Bottle, run, request, response, HTTPError

from speech_to_text import SpeechToText
from site_manager import SiteManager

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
        'http://localhost:8080', 'http://127.0.0.1:8080',
        'http://localhost:4322', 'http://127.0.0.1:4322',  # Added for Astro dev server
        'null'  # Allow file:// protocol for local HTML files
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
    website_builder_path = data.get("websiteBuilderPath", "")
    if website_builder_path:
        website_builder_path = urllib.parse.unquote(website_builder_path)
    
    if not name:
        raise HTTPError(400, "Site name is required")
    
    site = site_manager.create_site(name, description, website_builder_path)
    return {"site": site}

@app.get("/api/v1/sites/<site_id>")
def get_site(site_id):
    site = site_manager.get_site_config(site_id)
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
    return {
        "site_id": site_id,
        "id": page_id,
        "content": content
    }

@app.post("/api/v1/sites/<site_id>/pages")
def create_page(site_id):
    data = request.json or {}
    page_id = data.get("id")
    page_name = data.get("name")
    template = data.get("template", "")
    style = data.get("style", "")
    website_builder_path = data.get("websiteBuilderPath", "")
    if website_builder_path:
        website_builder_path = urllib.parse.unquote(website_builder_path)
    
    # Check if site exists and get its pages
    site = site_manager.get_site_config(site_id)
    if not site:
        raise HTTPError(404, "Site not found")
    
    success = site_manager.create_page(site_id, page_id, page_name, template, style, website_builder_path)
    if not success:
        raise HTTPError(400, "Failed to create page")
    
    response = {"page_id": page_id, "created": True}
    
    return response


@app.get("/api/v1/sites/<site_id>/pages/<page_id>")
def get_page(site_id, page_id):
    content = site_manager.get_page_content(site_id, page_id)
    if not content:
        raise HTTPError(404, "Page or site not found")

    return content

@app.put("/api/v1/sites/<site_id>/pages/<page_id>")
def update_page(site_id, page_id):
    logger.info(f"Updating page: {request}")
    data = request.json or {}
    content = data.get("content", "")
    logger.info(f"Page content: {content}")
    
    success = site_manager.update_page_content(site_id, page_id, content)
    if not success:
        raise HTTPError(404, "Page or site not found")
    
    return {"updated": True}

@app.get("/api/v1/sites/<site_id>/pages/<page_id>/editor_path")
def get_page_editor_path(site_id, page_id):
    """Get the absolute file path for a page"""
    site = site_manager.get_site_config(site_id)
    if not site:
        raise HTTPError(404, "Site not found")

    page_id_found = False
    for page in site.get("pages", []):
        if list(page.keys())[0] == page_id:
            page_id_found = True
            break
    if not page_id_found:
        raise HTTPError(404, "Page not found")

    page_path = site_manager.get_page_editor_path(site_id, page_id)
    absolute_path = page_path.resolve()

    return {
        "site_id": site_id,
        "page_id": page_id,
        "absolute_path": str(absolute_path),
        "exists": page_path.exists()
    }

@app.delete("/api/v1/sites/<site_id>/pages/<page_id>")
def delete_page(site_id, page_id):
    success = site_manager.delete_page(site_id, page_id)
    if not success:
        raise HTTPError(400, "Cannot delete page (not found or is index page)")

    return {"deleted": True}

# Page Modification Script Endpoints
@app.post("/api/v1/sites/<site_id>/pages/<page_id>/scripts")
def create_modification_script(site_id, page_id):
    data = request.json or {}
    script_content = data.get("script_content", "")
    script_name = data.get("script_name")
    
    if not script_content:
        raise HTTPError(400, "Script content is required")
    
    script_id = site_manager.create_page_modification_script(site_id, page_id, script_content, script_name)
    if not script_id:
        raise HTTPError(400, "Failed to create modification script")
    
    return {"script_id": script_id, "created": True}

# Components Endpoints
@app.get("/api/v1/components")
def list_components():
    """List all available components with their targets and parameters"""
    
    components = []
    components_dir = Path(__file__).parent / '../../ap-website-builder/components'
    
    # Find all XML files recursively
    xml_files = list(components_dir.glob('**/*.xml'))
    
    for xml_file in xml_files:
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component info
            component_id = xml_file.stem
            component_name = component_id.replace('-', ' ').replace('_', ' ').title()
            
            # Extract @target
            target_match = re.search(r'<!-- @target\s+(.+?)\s+-->', content)
            target = target_match.group(1) if target_match else None
            
            # Extract @param entries
            param_matches = re.findall(r'<!-- @param\s+(\w+)\s+-->', content)
            params = param_matches if param_matches else []
            
            # Get relative file path for loading content
            rel_path = xml_file.relative_to(Path(__file__).parent / '../../ap-website-builder')
            rel_path = str(rel_path).replace('\\', '/')  # Normalize path separators
            
            component_info = {
                'id': component_id,
                'name': component_name,
                'target': target,
                'params': params,
                'file_path': rel_path,
                'content': content
            }
            
            components.append(component_info)
            
        except Exception as e:
            logger.error(f"Failed to parse component {xml_file}: {e}")
            continue
    
    return {"components": components}

if __name__ == "__main__":
    # Listen only on localhost (127.0.0.1)
    run(app, host="127.0.0.1", port=8000, debug=True)

