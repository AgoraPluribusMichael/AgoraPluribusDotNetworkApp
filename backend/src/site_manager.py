import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import shutil
import re

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class SiteManager:
    def __init__(self, sites_directory="../sites"):
        self.sites_dir = Path(sites_directory)
        self.ensure_sites_directory()
    
    def ensure_sites_directory(self):
        if not self.sites_dir.exists():
            self.sites_dir.mkdir(parents=True, exist_ok=True)
    
    def get_site_path(self, site_id: str) -> Path:
        return self.sites_dir / site_id

    def get_site_editor_path(self, site_id: str) -> Path:
        return self.sites_dir / site_id / "editor"

    def get_page_editor_path(self, site_id: str, page_id: str) -> Path:
        return self.get_site_editor_path(site_id) / f"{page_id}.html"
    
    def get_site_config_path(self, site_id: str) -> Path:
        return self.get_site_path(site_id) / "site.json"

    def update_site_config(self, site_id: str, site_config: Dict) -> None:
        config_path = self.get_site_config_path(site_id)
        with config_path.open('w', encoding='utf-8') as f:
            json.dump(site_config, f, indent=2)
    
    def get_page_path(self, site_id: str, page_id: str) -> Path:
        return self.get_site_path(site_id) / f"{page_id}.html"
    
    def get_page_template_path(self, site_id: str, page_id: str) -> Path:
        return self.get_site_path(site_id) / "pages" / f"{page_id}.template"
    
    def get_page_scripts_dir(self, site_id: str) -> Path:
        return self.get_site_path(site_id) / "page_mod_scripts"
    
    def get_page_script_path(self, site_id: str, script_name: str) -> Path:
        return self.get_page_scripts_dir(site_id) / script_name
    
    def list_sites(self) -> List[Dict]:
        sites = []
        if not self.sites_dir.exists():
            return sites

        for item in self.sites_dir.iterdir():
            site_path = self.get_site_path(item.name)
            if site_path.is_dir():
                config_path = self.get_site_config_path(item.name)
                if config_path.exists():
                    try:
                        with config_path.open('r', encoding='utf-8') as f:
                            site_config = json.load(f)
                            sites.append(site_config)
                    except (json.JSONDecodeError, IOError):
                        continue
        return sites
    
    def get_site_config(self, site_id: str) -> Optional[Dict]:
        config_path = self.get_site_config_path(site_id)
        if not config_path.exists():
            return None

        try:
            with config_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def create_site(self, name: str, description: str = "", website_builder_path: str = "") -> Optional[Dict]:
        site_id = str(uuid.uuid4())

        # Create directories
        site_path = self.get_site_path(site_id)
        site_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Site path: {site_path}")

        editor_path = self.get_site_editor_path(site_id)
        editor_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Editor path: {editor_path}")

        # Copy page_mod_scripts directory from ap-website-builder
        source_scripts_path = Path(website_builder_path) / "page_mod_scripts.js"
        dest_scripts_path = editor_path / "page_mod_scripts.js"
        logger.info(f"source scripts path: {source_scripts_path}")
        logger.info(f"dest scripts path: {dest_scripts_path}")
        shutil.copy(source_scripts_path, dest_scripts_path)

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
        self.update_site_config(site_id, site_config)

        # Reload the config to get the updated pages array
        site_config = self.get_site_config(site_id)

        return site_config
    
    def update_site(self, site_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict]:
        site_config = self.get_site_config(site_id)
        if not site_config:
            return None
        
        # Update fields
        if name is not None:
            site_config["name"] = name
        if description is not None:
            site_config["description"] = description
        site_config["updated_at"] = datetime.now().isoformat()
        
        # Save updated configuration
        self.update_site_config(site_id, site_config)
        
        return site_config
    
    def delete_site(self, site_id: str) -> bool:
        site_path = self.get_site_path(site_id)
        if not site_path.exists():
            return False
        
        try:
            shutil.rmtree(site_path)
            return True
        except OSError:
            return False
    
    def list_pages(self, site_id: str) -> List[Dict]:
        site_config = self.get_site_config(site_id)
        if not site_config:
            return []
        
        pages = []
        site_editor_dir = self.get_site_editor_path(site_id)

        for page in site_config.get("pages", []):
            page_id = list(page.keys())[0]
            page_name = page[page_id]
            page_path = site_editor_dir / f"{page_id}.html"
            if page_path.exists():
                stat = page_path.stat()
                pages.append({
                    "id": page_id,
                    "name": page_name,
                    "site_id": site_id,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return pages
    
    def get_page_content(self, site_id: str, page_id: str) -> Optional[str]:
        page_path = self.get_page_editor_path(site_id, page_id)
        logger.info(f"Page path: {page_path.absolute()}")
        if not page_path.exists():
            return None

        try:
            with page_path.open('r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Retrieved content: {content}")
                return content
        except IOError:
            return None
    
    def get_page_template(self, site_id: str, page_id: str) -> Optional[str]:
        template_path = self.get_page_template_path(site_id, page_id)
        if not template_path.exists():
            return None

        try:
            with template_path.open('r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return None
    
    def create_page(self, site_id: str, page_id: str, page_name: str, template: str = "", style: str = "", website_builder_path: str = "") -> bool:
        logger.info(f"CREATING PAGE: {site_id}: {page_id}, {page_name}, {template}, {style}")

        # Add page to site config if not already there
        site_config = self.get_site_config(site_id)
        if {page_id: page_name} not in site_config.get("pages", []):
            site_config["pages"].append({page_id: page_name})
            site_config["updated_at"] = datetime.now().isoformat()
            self.update_site_config(site_id, site_config)

        editor_path: Path = self.get_site_editor_path(site_id)
        try:
            # Create index.html from template
            source_template_path = Path(website_builder_path) / "templates" / f"{template}.html"
            logger.info(f"Source template: {source_template_path}")
            with source_template_path.open('r', encoding='utf-8') as f:
                content = f.read()
                content = content.replace("${PAGE_ID}", page_id)
                logger.info(f"content: {content}")
            page_path = editor_path / f"{page_id}.html"
            logger.info(f"Destination template: {page_path}")
            with page_path.open('w', encoding='utf-8') as f:
                f.write(content)

            # Copy style from template
            source_style_path = Path(website_builder_path) / "styles" / f"{style}.css"
            dest_style_path = editor_path / f"{page_id}.css"
            if source_style_path.exists():
                shutil.copy2(source_style_path, dest_style_path)

            return True
        except Exception as e:
            logger.exception(e)
            return False
    
    def update_page_content(self, site_id: str, page_id: str, content: str) -> bool:
        # Verify site exists and page is registered
        site_config = self.get_site_config(site_id)

        page_path = self.get_page_editor_path(site_id, page_id)
        try:
            with page_path.open('w', encoding='utf-8') as f:
                f.write(content)

            # Update site's modified time
            site_config["updated_at"] = datetime.now().isoformat()
            self.update_site_config(site_id, site_config)
            
            return True
        except IOError:
            return False
    
    def delete_page(self, site_id: str, page_id: str) -> bool:
        site_config = self.get_site_config(site_id)
        if not site_config or page_id not in site_config.get("pages", []):
            return False
        
        page_path = self.get_page_path(site_id, page_id)
        template_path = self.get_page_template_path(site_id, page_id)
        try:
            # Remove from config
            site_config["pages"].remove(page_id)
            site_config["updated_at"] = datetime.now().isoformat()

            self.update_site_config(site_id, site_config)

            # Remove HTML file
            if page_path.exists():
                page_path.unlink()

            # Remove template file
            if template_path.exists():
                template_path.unlink()
            
            return True
        except (OSError, ValueError):
            return False