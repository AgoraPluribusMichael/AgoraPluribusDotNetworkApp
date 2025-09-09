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
            "pages": []  # Start with empty pages array
        }
        
        # Save configuration first
        config_path = self.get_site_config_path(site_id)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(site_config, f, indent=2)
        
        # Now create initial index.html page (this will update the pages array)
        self.create_page(site_id, "index", "")
        
        # Reload the config to get the updated pages array
        site_config = self.get_site(site_id)
        
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
    
    def _generate_html_from_template(self, template: str, site_config: Dict, page_id: str) -> str:
        """Generate Astro content based on template type from template files"""
        site_name = site_config.get('name', 'My Website')
        year = datetime.now().year
        
        # Try to load Astro template from file
        template_path = os.path.join(os.path.dirname(__file__), 'page_templates', f'{template}.astro')
        
        if template and os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    astro_content = f.read()
                
                # Generate the component usage with props
                astro_page = f"""---
import Template from '../page_templates/{template}.astro';

const props = {{
  title: "{site_name} - {page_id.capitalize()}",
  name: "{page_id}",
  copyright: "{year} {site_name}. All rights reserved.",
  gtag: undefined
}};
---

<Template {{...props}}>
  <div slot="navbar-menu-button">
    <a href="#home">Home</a>
    <a href="#about">About</a>
    <a href="#services">Services</a>
    <a href="#contact">Contact</a>
  </div>
  
  <div slot="panel-content">
    <h2>Welcome to {page_id.capitalize()} Page</h2>
    <p>This is your new {page_id} page created from the {template} template. Start editing to add your content!</p>
    
    <section>
      <h3>Getting Started</h3>
      <p>This page is generated from an Astro template. You can customize this content to suit your needs.</p>
    </section>
    
    <section>
      <h3>Add Your Content</h3>
      <p>Replace this placeholder text with your own content. You can add images, links, and more Astro components as needed.</p>
    </section>
  </div>
  
  <div slot="footer-text">
    <p>Contact us: info@{site_name.lower().replace(' ', '')}.com</p>
  </div>
  
  <div slot="copyright">
    {year} {site_name}
  </div>
  
  <div slot="footer-text-floating">
    <p>Built with Astro • {site_name}</p>
  </div>
</Template>"""
                
                return astro_page
            except IOError:
                pass  # Fall through to default template
        
        # Default HTML template if no Astro template found
        default_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_name} - {page_id.capitalize()}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        header h1 {{
            margin: 0;
            font-size: 2.5rem;
            text-align: center;
        }}
        nav {{
            background-color: white;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        nav ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            gap: 2rem;
        }}
        nav a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }}
        nav a:hover {{
            color: #764ba2;
        }}
        main {{
            background-color: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            min-height: 400px;
        }}
        .hero {{
            text-align: center;
            padding: 3rem 0;
        }}
        .hero h2 {{
            font-size: 2rem;
            color: #333;
            margin-bottom: 1rem;
        }}
        .hero p {{
            font-size: 1.2rem;
            color: #666;
            max-width: 600px;
            margin: 0 auto;
        }}
        .content-section {{
            margin: 2rem 0;
        }}
        .content-section h3 {{
            color: #667eea;
            margin-bottom: 1rem;
        }}
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem 0;
            color: #666;
            background-color: white;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{site_name}</h1>
        </div>
    </header>
    
    <div class="container">
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
        
        <main>
            <section class="hero">
                <h2>Welcome to {page_id.capitalize()} Page</h2>
                <p>This is your new {page_id} page. Start editing to add your content!</p>
            </section>
            
            <section class="content-section">
                <h3>Getting Started</h3>
                <p>This is a starter template for your new page. You can customize this content to suit your needs.</p>
            </section>
            
            <section class="content-section">
                <h3>Add Your Content</h3>
                <p>Replace this placeholder text with your own content. You can add images, links, and more HTML elements as needed.</p>
            </section>
        </main>
        
        <footer>
            <p>&copy; {year} {site_name}. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>"""
        
        return default_html
    
    def create_page(self, site_id: str, page_id: str, template: str = "") -> bool:
        site_config = self.get_site(site_id)
        if not site_config:
            return False
        
        # Add page to site config if not already there
        if page_id not in site_config.get("pages", []):
            site_config["pages"].append(page_id)
            site_config["updated_at"] = datetime.now().isoformat()
            
            config_path = self.get_site_config_path(site_id)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(site_config, f, indent=2)
        
        # Ensure pages directory exists
        pages_dir = os.path.join(self.get_site_path(site_id), "pages")
        os.makedirs(pages_dir, exist_ok=True)
        
        # Store template file
        template_path = self.get_page_template_path(site_id, page_id)
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template if template else "")
        except IOError:
            return False
        
        # Generate initial HTML content based on template type
        initial_html = self._generate_html_from_template(template, site_config, page_id)
        
        # Store HTML content
        page_path = self.get_page_path(site_id, page_id)
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(initial_html)
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