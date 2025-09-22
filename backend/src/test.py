import site_manager

if __name__ == "__main__":
    site_manager_obj = site_manager.SiteManager()
    page_editor_path = site_manager_obj.get_page_editor_path("2b1ccdcb-c60e-4d67-9692-44b7784eed58", "index")
    print(page_editor_path)