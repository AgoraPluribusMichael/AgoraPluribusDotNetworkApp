import { marked } from 'marked';

interface TemplateData {
  [key: string]: string;
}

interface CustomElement {
  pattern: string;
  template: string;
}

export class TemplateProcessor {
  private customElements: { [key: string]: CustomElement } = {};
  private templates: { [key: string]: string } = {};

  async loadCustomElements(): Promise<void> {
    try {
      const response = await fetch('/templates/custom_elements.json');
      this.customElements = await response.json();
    } catch (error) {
      console.error('Failed to load custom elements:', error);
    }
  }

  async loadTemplate(templateName: string): Promise<string> {
    if (this.templates[templateName]) {
      return this.templates[templateName];
    }

    try {
      const response = await fetch(`/templates/${templateName}.xml`);
      const template = await response.text();
      this.templates[templateName] = template;
      return template;
    } catch (error) {
      console.error(`Failed to load template ${templateName}:`, error);
      return '';
    }
  }

  async processTemplate(template: string, data: TemplateData): Promise<string> {
    let processed = template;

    // Replace ${variable} placeholders
    Object.keys(data).forEach(key => {
      const placeholder = `\${${key}}`;
      processed = processed.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), data[key]);
    });

    // Process custom elements
    for (const elementName of Object.keys(this.customElements)) {
      const element = this.customElements[elementName];
      const regex = new RegExp(element.pattern, 'g');
      
      let match;
      while ((match = regex.exec(processed)) !== null) {
        try {
          const elementTemplate = await this.loadTemplate(element.template);
          const elementData = { content: match[1] || match[0] };
          const processedElement = await this.processTemplate(elementTemplate, elementData);
          processed = processed.replace(match[0], processedElement);
        } catch (error) {
          console.error(`Error processing custom element ${elementName}:`, error);
        }
      }
    }

    return processed;
  }

  async processMarkdownToTemplate(markdown: string, templateName: string): Promise<string> {
    const template = await this.loadTemplate(templateName);
    const htmlContent = await marked(markdown);
    
    // Support both ${content} and ${body} placeholders for compatibility
    const result = await this.processTemplate(template, { 
      content: htmlContent, 
      body: htmlContent 
    });
    
    console.log('Template processing:', {
      templateName,
      template: template.substring(0, 100) + '...',
      markdown: markdown.substring(0, 50) + '...',
      htmlContent: htmlContent.substring(0, 100) + '...',
      result: result.substring(0, 100) + '...'
    });
    
    return result;
  }
}

export const templateProcessor = new TemplateProcessor();