import json
import xml.etree.ElementTree as ET
import re

def isEpisode(element):
    if element.tag != "item":
        return False
    is_episode = False
    content = ""
    for child in element.iter():
        if child.tag == "link":
            link = child.text.strip()
            if re.match(".*[0-9]{4}/[0-9]{2}/[0-9]{2}.*", link):
                is_episode = True
        if "content" in child.tag and "encoded" in child.tag:
            content = child.text
            if content:
                content = content.strip()
    if is_episode:
        return content
    else:
        return None

if __name__ == "__main__":
    tree = ET.parse('worldxppodcast.xml')
    root = tree.getroot()
    episode_list = list()
    for element in root.iter():
        if element.tag == 'item':
            content = isEpisode(element)
            if content:
                episode_list.append(content)
    with open("episodes.json", "w") as f:
        json.dump(episode_list, f, indent=2)