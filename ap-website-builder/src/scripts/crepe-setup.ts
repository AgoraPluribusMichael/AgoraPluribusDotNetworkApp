import { Crepe } from "@milkdown/crepe";
import { marked } from "marked";
import "@milkdown/crepe/theme/common/style.css";
import "@milkdown/crepe/theme/frame.css"; // or classic, nord, etc.

export const initCrepe = () => {
  const crepe = new Crepe({
    root: "#app",
    defaultValue: "Hello, Milkdown!",
  });

  crepe.create().then(() => {
    console.log("Editor created");
  });

  return crepe;
};

export const crepe = initCrepe();

const button = document.createElement("button");
button.innerText = "Export Markdown";
button.onclick = async () => {
  const md = await crepe.getMarkdown();
  console.log("Markdown content:", md);
  alert(md); // show it for demo
  const html = marked(md);
  alert(html);
};

document.body.appendChild(button);

