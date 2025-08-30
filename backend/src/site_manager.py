import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class SiteManager:
    def __init__(self, sites_directory="sites"):
        self.sites_dir = sites_directory
        self.ensure_sites_directory()
    
    def ensure_sites_directory(self):
        if not os.path.exists(self.sites_dir):
            os.makedirs(self.sites_dir)
    
    def get_site_path(self, site_id: str) -> str:
        return os.path.join(self.sites_dir, site_id)
    
    def get_site_config_path(self, site_id: str) -> str:
        return os.path.join(self.get_site_path(site_id), "site.json")
    
    def get_page_path(self, site_id: str, page_id: str) -> str:
        return os.path.join(self.get_site_path(site_id), "pages", f"{page_id}.html")
    
    def get_page_template_path(self, site_id: str, page_id: str) -> str:
        return os.path.join(self.get_site_path(site_id), "pages", f"{page_id}.template")
    
    def list_sites(self) -> List[Dict]:
        sites = []
        if not os.path.exists(self.sites_dir):
            return sites
            
        for item in os.listdir(self.sites_dir):
            site_path = self.get_site_path(item)
            if os.path.isdir(site_path):
                config_path = self.get_site_config_path(item)
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            site_config = json.load(f)
                            sites.append(site_config)
                    except (json.JSONDecodeError, IOError):
                        continue
        return sites
    
    def get_site(self, site_id: str) -> Optional[Dict]:
        config_path = self.get_site_config_path(site_id)
        if not os.path.exists(config_path):
            return None
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def create_site(self, name: str, description: str = "") -> Dict:
        site_id = str(uuid.uuid4())
        site_path = self.get_site_path(site_id)
        pages_path = os.path.join(site_path, "pages")
        
        # Create directories
        os.makedirs(pages_path, exist_ok=True)
        
        # Create site configuration
        site_config = {
            "id": site_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "pages": ["index"]  # Default index page
        }
        
        # Save configuration
        config_path = self.get_site_config_path(site_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(site_config, f, indent=2)
        
        return site_config
    
    def update_site(self, site_id: str, name: str = None, description: str = None) -> Optional[Dict]:
        site_config = self.get_site(site_id)
        if not site_config:
            return None
        
        # Update fields
        if name is not None:
            site_config["name"] = name
        if description is not None:
            site_config["description"] = description
        site_config["updated_at"] = datetime.now().isoformat()
        
        # Save updated configuration
        config_path = self.get_site_config_path(site_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(site_config, f, indent=2)
        
        return site_config
    
    def delete_site(self, site_id: str) -> bool:
        site_path = self.get_site_path(site_id)
        if not os.path.exists(site_path):
            return False
        
        try:
            import shutil
            shutil.rmtree(site_path)
            return True
        except OSError:
            return False
    
    def list_pages(self, site_id: str) -> List[Dict]:
        site_config = self.get_site(site_id)
        if not site_config:
            return []
        
        pages = []
        pages_dir = os.path.join(self.get_site_path(site_id), "pages")
        
        for page_id in site_config.get("pages", []):
            page_path = os.path.join(pages_dir, f"{page_id}.html")
            if os.path.exists(page_path):
                stat = os.stat(page_path)
                pages.append({
                    "id": page_id,
                    "site_id": site_id,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return pages
    
    def get_page_content(self, site_id: str, page_id: str) -> Optional[str]:
        page_path = self.get_page_path(site_id, page_id)
        if not os.path.exists(page_path):
            return None
        
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return None
    
    def get_page_template(self, site_id: str, page_id: str) -> Optional[str]:
        template_path = self.get_page_template_path(site_id, page_id)
        if not os.path.exists(template_path):
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return None
    
    def create_page(self, site_id: str, page_id: str, template: str = "") -> bool:
        site_config = self.get_site(site_id)
        if not site_config:
            return False
        
        # Add page to site config if not already there
        if page_id not in site_config.get("pages", []):
            site_config["pages"].append(page_id)
            site_config["template"] = template
            site_config["updated_at"] = datetime.now().isoformat()
            
            config_path = self.get_site_config_path(site_id)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(site_config, f, indent=2)
        
        # Store template file
        template_path = self.get_page_template_path(site_id, page_id)
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write("")
        except IOError:
            return False
        
        # Generate and store HTML content (for now, just use template as HTML)
        page_path = self.get_page_path(site_id, page_id)
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(template)  # TODO: Process template to generate actual HTML
            return True
        except IOError:
            return False
    
    def update_page_content(self, site_id: str, page_id: str, content: str) -> bool:
        # Verify site exists and page is registered
        site_config = self.get_site(site_id)
        if not site_config or page_id not in site_config.get("pages", []):
            return False
        
        page_path = self.get_page_path(site_id, page_id)
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update site's modified time
            site_config["updated_at"] = datetime.now().isoformat()
            config_path = self.get_site_config_path(site_id)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(site_config, f, indent=2)
            
            return True
        except IOError:
            return False
    
    def delete_page(self, site_id: str, page_id: str) -> bool:
        site_config = self.get_site(site_id)
        if not site_config or page_id not in site_config.get("pages", []):
            return False
        
        page_path = self.get_page_path(site_id, page_id)
        template_path = self.get_page_template_path(site_id, page_id)
        try:
            # Remove from config
            site_config["pages"].remove(page_id)
            site_config["updated_at"] = datetime.now().isoformat()
            
            config_path = self.get_site_config_path(site_id)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(site_config, f, indent=2)
            
            # Remove HTML file
            if os.path.exists(page_path):
                os.remove(page_path)
            
            # Remove template file
            if os.path.exists(template_path):
                os.remove(template_path)
            
            return True
        except (OSError, ValueError):
            return False