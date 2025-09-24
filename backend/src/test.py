from pathlib import Path
if __name__ == "__main__":
    site_editor_path = r"..\sites\418c8faf-3c43-4b29-975c-9af1c20eadf8\editor"
    page_id = "home"
    pathlist = Path(site_editor_path).glob(f'**/{page_id}.[a-z]*')
    for path in pathlist:
        print(path)