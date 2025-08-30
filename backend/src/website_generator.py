import os
import json
import re

DIR_TEMPLATES = "templates"
DIR_PAGES = "pages"
TEMPLATES_DICT = dict()

# Read HTML templates
for dirpath, _, filenames in os.walk(DIR_TEMPLATES):
    for filename in filenames:
        with open(f"{dirpath}{os.sep}{filename}", encoding="utf-8") as template_file:
            template_name = filename.split(".")[0]
            TEMPLATES_DICT[template_name] = template_file.read()

# Load custom html elements
CUSTOM_ELEMENTS_DICT = dict()  # key: compiled regex pattern, value: html template string
with open(f"{DIR_TEMPLATES}{os.sep}custom_elements.json", encoding="utf-8") as custom_elements_file:
    custom_elements_defs = json.load(custom_elements_file)
    for custom_element_name in custom_elements_defs:
        pattern = custom_elements_defs[custom_element_name]["pattern"]
        pattern = re.compile(pattern)
        template = custom_elements_defs[custom_element_name]["template"]
        CUSTOM_ELEMENTS_DICT[pattern] = TEMPLATES_DICT[template]

def generate_element_from_template(template, fields_dict):
    with open(template, "r", encoding="utf-8") as template_file:
        element = template_file.read()

    for field in fields_dict:
        replace_string = fields_dict[field]
        if replace_string:
            element = element.replace(f"${{{field}}}", replace_string)
    return element

def generate_element_from_template_html(template, html_path):
    print(template, html_path)
    with open(template, "r", encoding="utf-8") as template_file:
        element = template_file.read()

    with open(html_path, "r", encoding="utf-8") as html_file:
        inner_html = html_file.read()

    return element.replace("${body}", inner_html)

def generate_page(pages_directory, page_name):
    page_directory = f"{pages_directory}{os.sep}{page_name}"

    with open(f"{page_directory}{os.sep}template.html", "r", encoding="utf-8") as template_file:
        page_html = template_file.read()

    with open(f"{page_directory}/components.json", encoding="utf-8") as components_file:
        components_dict = json.load(components_file)

    head = components_dict["head"]
    head_template = head["template"]
    head_fields_dict = head["fields"]
    head_element = generate_element_from_template(head_template, head_fields_dict)

    body = components_dict["body"]
    panel_element_list = list()
    for panel in body:
        panel_template = panel["template"]
        panel_content_path = panel["content_path"]
        panel_element = generate_element_from_template_html(panel_template, panel_content_path)
        panel_element_list.append(panel_element)
    panel_element = '\n'.join(panel_element_list)

    footer = components_dict["footer"]
    footer_template = footer["template"]
    footer_content_path = footer["content_path"]
    footer_element = generate_element_from_template_html(footer_template, footer_content_path)

    copyright = components_dict["copyright"]
    copyright_template = copyright["template"]
    copyright_fields_dict = copyright["fields"]
    copyright_element = generate_element_from_template(copyright_template, copyright_fields_dict)

    page_html = (
        page_html
        .replace("${head}", head_element)
        .replace("${panels}", panel_element)
        .replace("${footer_floating}", footer_element)
        .replace("${copyright_container}", copyright_element)
    )

    # for custom_element_pattern in CUSTOM_ELEMENTS_DICT:
    #     result = custom_element_pattern.search(page_html)
    #     while result:
    #         video_id = result.group(1)
    #         custom_element_html = TEMPLATES_DICT["youtube_embed"].replace("${video_id}", video_id)
    #         page_html = re.sub(custom_element_pattern, custom_element_html, page_html, count=1)
    #         result = custom_element_pattern.search(page_html)

    page_html = page_html.replace("<a href", '<a target="_blank" href')
    # GENERATE NAVBAR
    navbar_element = TEMPLATES_DICT["navbar"]
    buttons_list = list()
    for page_name in os.listdir(DIR_PAGES):
        button = TEMPLATES_DICT["navbar_menu_button"]
        button = (
            button
            .replace("${href}", f"{page_name}.html")
            .replace("${label}", components_dict["head"]["fields"]["title"])
        )
        buttons_list.append(button)
    navbar_element = navbar_element.replace("${buttons}", "".join(buttons_list))

    page_html = page_html.replace("${navbar}", navbar_element)

    return page_html

def generate_editor(pages_directory, page_name):
    # Generate static pages
    for page_name in os.listdir(DIR_PAGES):
        index_html = generate_page(DIR_PAGES, page_name)
        with open(f"{page_name}.html", "w", encoding="utf-8") as html_file:
            html_file.write(index_html)

    # Generate editors
    for page_name in os.listdir(DIR_PAGES):
        pass

if __name__ == "__main__":
    for page_name in os.listdir(DIR_PAGES):
        index_html = generate_page(DIR_PAGES, page_name)
        with open(f"{page_name}.html", "w", encoding="utf-8") as html_file:
            html_file.write(index_html)