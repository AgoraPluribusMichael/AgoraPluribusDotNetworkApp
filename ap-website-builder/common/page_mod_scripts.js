/**
 * Site Modification UI - Component Insertion System
 * This file handles the insertion of component UI elements based on DOM targets
 */

class SiteModificationUI {
    constructor() {
        this.components = [];
        this.targetComponentMap = new Map(); // Map targets to their components
        this.insertionButtons = [];
        this.siteId = null;
        this.pageId = null;
    }

    /**
     * Initialize the component system
     */
    async init() {
        try {
            await this.loadComponents();
            this.groupComponentsByTarget();
            this.injectInsertionButtons();
            const pathnameComps = window.location.pathname.split('/');
            const editorIndex = pathnameComps.indexOf("editor");
            this.siteId = pathnameComps[editorIndex-1];
            this.pageId = pathnameComps[editorIndex+1];
            this.pageId = this.pageId.split('.')[0];
        } catch (error) {
            console.error('Failed to initialize Site Modification UI:', error);
        }
    }

    /**
     * Load all components from the API
     */
    async loadComponents() {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/v1/components');
            const data = await response.json();
            this.components = data.components;
            console.log('Loaded components:', this.components);
        } catch (error) {
            console.error('Failed to load components:', error);
            throw error;
        }
    }

    /**
     * Group components by their target selectors
     */
    groupComponentsByTarget() {
        this.targetComponentMap.clear();
        
        this.components.forEach(component => {
            if (component.target) {
                if (!this.targetComponentMap.has(component.target)) {
                    this.targetComponentMap.set(component.target, []);
                }
                this.targetComponentMap.get(component.target).push(component);
            }
        });

        console.log('Components grouped by target:', this.targetComponentMap);
    }

    /**
     * Inject insertion buttons into the page based on component targets
     */
    injectInsertionButtons() {
        // Remove existing buttons
        this.removeInsertionButtons();

        this.targetComponentMap.forEach((components, target) => {
            this.injectButtonsForTarget(target, components);
        });

        // Also inject edit buttons for editable elements
        this.injectEditButtons();
    }

    async saveAndReloadPage() {
        // Remove existing buttons
        this.removeInsertionButtons();

        // Send the HTML to the backend to save
        const response = await fetch(`http://127.0.0.1:8000/api/v1/sites/${this.siteId}/pages/${this.pageId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        this.targetComponentMap.forEach((components, target) => {
            this.injectButtonsForTarget(target, components);
        });

        // Also re-inject edit buttons
        this.injectEditButtons();
    }

    /**
     * Inject buttons for a specific target
     * @param {string} target - The target selector (e.g., "main#main-article:child")
     * @param {Array} components - Components that match this target
     */
    injectButtonsForTarget(target, components) {
        try {
            // Parse target selector (e.g., "main#main-article:child" -> selector: "main#main-article", position: "child")
            const [selector, position] = target.split(':');
            const targetElements = document.querySelectorAll(selector);

            targetElements.forEach((element, elementIndex) => {
                // Get element position for button placement
                const rect = element.getBoundingClientRect();
                
                // Create insertion button
                const button = document.createElement('button');
                button.className = 'component-insertion-button';
                button.innerHTML = `+ Add Component (${components.length})`;

                // Position button based on target position
                if (position === 'child') {
                    // Inside the element
                    button.style.left = (rect.left + 10) + 'px';
                    button.style.top = (rect.top + 10) + 'px';
                } else {
                    // Outside/before the element
                    button.style.left = (rect.left + 10) + 'px';
                    button.style.top = (rect.top - 30) + 'px';
                }

                // Add click event to show component selection modal
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showComponentSelectionModal(target, components, element);
                });

                // Add button to page
                document.body.appendChild(button);
            });

        } catch (error) {
            console.error(`Failed to inject buttons for target ${target}:`, error);
        }
    }

    /**
     * Remove all insertion buttons
     */
    removeInsertionButtons() {
        this.insertionButtons = document.getElementsByClassName("component-insertion-button");
        for (let i=this.insertionButtons.length-1; i >= 0; i--) {
            this.insertionButtons[i].remove();
        }

        // Also remove edit buttons
        const editButtons = document.getElementsByClassName("component-edit-button");
        for (let i=editButtons.length-1; i >= 0; i--) {
            editButtons[i].remove();
        }
    }

    /**
     * Show component selection modal
     * @param {string} target - The target selector
     * @param {Array} components - Available components for this target
     * @param {Element} targetElement - The target DOM element
     */
    showComponentSelectionModal(target, components, targetElement) {
        const modal = this.createComponentSelectionModal(target, components, targetElement);
        document.body.appendChild(modal);
    }

    /**
     * Create component selection modal
     */
    createComponentSelectionModal(target, components, targetElement) {
        const modal = document.createElement('div');
        modal.className = 'component-selection-modal';

        const modalContent = document.createElement('div');
        modalContent.classList.add('component-panel');

        modalContent.innerHTML = `
            <h3>Select Component to Insert</h3>
            <div class="component-list"></div>
            <button class="close-modal-btn">Cancel</button>
        `;

        const componentList = modalContent.querySelector('.component-list');

        // Add component options
        components.forEach(component => {
            const componentOption = document.createElement('div');
            
            componentOption.innerHTML = `
                <p>${component.name}</p>
            `;

            componentOption.addEventListener('click', () => {
                modal.remove();
                this.insertComponent(component, {}, targetElement);
            });

            componentOption.addEventListener('mouseenter', () => {
                componentOption.style.backgroundColor = '#686868';
            });

            componentOption.addEventListener('mouseleave', () => {
                componentOption.style.backgroundColor = '';
            });

            componentList.appendChild(componentOption);
        });

        // Close modal functionality
        const closeBtn = modalContent.querySelector('.close-modal-btn');
        closeBtn.addEventListener('click', () => modal.remove());
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        modal.appendChild(modalContent);
        return modal;
    }

    /**
     * Inject edit buttons for all visible editable elements
     */
    injectEditButtons() {
        try {
            // Find all visible elements with the "editable" class
            const editableElements = document.querySelectorAll('.editable');

            editableElements.forEach(element => {
                // Check if element is visible
                const rect = element.getBoundingClientRect();
                const style = window.getComputedStyle(element);

                if (rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden') {
                    this.createEditButton(element);
                }
            });
        } catch (error) {
            console.error('Failed to inject edit buttons:', error);
        }
    }

    /**
     * Create an edit button for an editable element
     * @param {Element} element - The editable element
     */
    createEditButton(element) {
        try {
            const rect = element.getBoundingClientRect();

            // Create edit button
            const button = document.createElement('button');
            button.className = 'component-edit-button';
            button.innerHTML = '✏️ Edit';

            // Add click event to show appropriate edit modal
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.showEditModal(element);
            });

            // Add button to page
            element.appendChild(button);
        } catch (error) {
            console.error('Failed to create edit button:', error);
        }
    }

    /**
     * Show edit modal based on element type
     * @param {Element} element - The editable element
     */
    async showEditModal(element) {
        try {
            // Get the editable type from the element's classes
            const classList = Array.from(element.classList);
            const editableType = classList.find(cls => cls.startsWith('editable-')) || 'editable-text';

            let modal;
            switch (editableType) {
                case 'editable-text':
                    modal = this.createTextEditModal(element);
                    break;
                case 'editable-markdown':
                    modal = await this.createMarkdownEditModal(element);
                    break;
                default:
                    modal = this.createTextEditModal(element);
                    break;
            }

            // Only append modal to body if one was created (text editing is now inline)
            if (modal) {
                document.body.appendChild(modal);
            }
        } catch (error) {
            console.error('Failed to show edit modal:', error);
        }
    }

    /**
     * Create inline text editor
     * @param {Element} element - The editable element
     */
    createTextEditModal(element) {
        // Get the current text content (excluding the edit button)
        const editButton = element.querySelector('.component-edit-button');
        const currentText = element.textContent.replace('✏️ Edit', '').trim();

        // Store original content and hide edit button
        const originalContent = element.innerHTML;
        editButton.style.display = 'none';

        // Create textarea
        const textarea = document.createElement('textarea');
        textarea.className = "editable-textarea";
        textarea.value = currentText;

        // Replace element content with textarea
        element.innerHTML = '';
        element.appendChild(textarea);

        // Focus the textarea
        textarea.focus();
        textarea.select();

        // Handle Enter key to save
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                saveChanges();
            } else if (e.key === 'Escape') {
                cancelEdit();
            }
        });

        // Handle blur to save
        textarea.addEventListener('blur', () => {
            saveChanges();
        });

        const saveChanges = () => {
            const newContent = textarea.value.trim();
            element.innerHTML = originalContent;

            // Update the text content while preserving the edit button
            const editButton = element.querySelector('.component-edit-button');
            element.childNodes.forEach(node => {
                if (node !== editButton && node.nodeType === Node.TEXT_NODE) {
                    node.textContent = newContent;
                } else if (node !== editButton && node.nodeType === Node.ELEMENT_NODE && !node.classList.contains('component-edit-button')) {
                    node.textContent = newContent;
                }
            });

            // If no text nodes exist, create one
            if (!element.textContent.includes(newContent)) {
                const textNode = document.createTextNode(newContent);
                element.insertBefore(textNode, editButton);
            }

            editButton.style.display = '';
            setTimeout(() => this.savePage(), 100);
        };

        const cancelEdit = () => {
            element.innerHTML = originalContent;
            const editButton = element.querySelector('.component-edit-button');
            editButton.style.display = '';
        };

        // Return null since we're not creating a modal
        return null;
    }

    /**
     * Load EasyMDE dependencies dynamically
     */
    async loadEasyMDE() {
        console.log("Load EasyMDE");

        // Check if EasyMDE is already loaded
        if (typeof EasyMDE !== 'undefined') {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            // Load CSS first
            if (!document.querySelector('link[href*="easymde.min.css"]')) {
                const cssLink = document.createElement('link');
                cssLink.rel = 'stylesheet';
                cssLink.href = '../common/easymde.min.css';
                document.head.appendChild(cssLink);
            }

            // Load JS
            if (!document.querySelector('script[src*="easymde"]')) {
                const script = document.createElement('script');
                script.src = '../common/easymde.min.js';
                script.onload = () => {
                    console.log('EasyMDE script loaded');
                    // Wait for EasyMDE to be available
                    const checkEasyMDE = () => {
                        if (typeof EasyMDE !== 'undefined') {
                            console.log('EasyMDE global variable available');
                            resolve();
                        } else {
                            console.log('Waiting for EasyMDE to initialize...');
                            setTimeout(checkEasyMDE, 100);
                        }
                    };
                    checkEasyMDE();
                };
                script.onerror = () => {
                    console.error('Failed to load EasyMDE script');
                    reject(new Error('Failed to load EasyMDE'));
                };
                document.head.appendChild(script);
            } else {
                // Script already exists, check if EasyMDE is available
                const checkExisting = () => {
                    if (typeof EasyMDE !== 'undefined') {
                        resolve();
                    } else {
                        setTimeout(checkExisting, 100);
                    }
                };
                checkExisting();
            }
        });
    }

    /**
     * Convert HTML to markdown
     * @param {string} html - The HTML text to convert
     * @returns {string} - The markdown representation
     */
    htmlToMarkdown(html) {
        return html
            // Headers
            .replace(/<h1[^>]*>(.*?)<\/h1>/gim, '# $1\n\n')
            .replace(/<h2[^>]*>(.*?)<\/h2>/gim, '## $1\n\n')
            .replace(/<h3[^>]*>(.*?)<\/h3>/gim, '### $1\n\n')
            .replace(/<h4[^>]*>(.*?)<\/h4>/gim, '#### $1\n\n')
            .replace(/<h5[^>]*>(.*?)<\/h5>/gim, '##### $1\n\n')
            .replace(/<h6[^>]*>(.*?)<\/h6>/gim, '###### $1\n\n')

            // Bold and italic
            .replace(/<strong[^>]*>(.*?)<\/strong>/gim, '**$1**')
            .replace(/<b[^>]*>(.*?)<\/b>/gim, '**$1**')
            .replace(/<em[^>]*>(.*?)<\/em>/gim, '*$1*')
            .replace(/<i[^>]*>(.*?)<\/i>/gim, '*$1*')

            // Links
            .replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gim, '[$2]($1)')

            // Images
            .replace(/<img[^>]*alt="([^"]*)"[^>]*src="([^"]*)"[^>]*\/?>/gim, '![$1]($2)')
            .replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*\/?>/gim, '![$2]($1)')
            .replace(/<img[^>]*src="([^"]*)"[^>]*\/?>/gim, '![]($1)')

            // Lists
            .replace(/<ul[^>]*>/gim, '')
            .replace(/<\/ul>/gim, '\n')
            .replace(/<ol[^>]*>/gim, '')
            .replace(/<\/ol>/gim, '\n')
            .replace(/<li[^>]*>(.*?)<\/li>/gim, '- $1\n')

            // Paragraphs and line breaks
            .replace(/<p[^>]*>/gim, '')
            .replace(/<\/p>/gim, '\n\n')
            .replace(/<br[^>]*\/?>/gim, '\n')
            .replace(/<div[^>]*>/gim, '')
            .replace(/<\/div>/gim, '\n')

            // Code
            .replace(/<code[^>]*>(.*?)<\/code>/gim, '`$1`')
            .replace(/<pre[^>]*>(.*?)<\/pre>/gims, '```\n$1\n```\n')

            // Blockquotes
            .replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gims, (match, content) => {
                return content.split('\n').map(line => '> ' + line.trim()).join('\n') + '\n\n';
            })

            // Remove any remaining HTML tags
            .replace(/<[^>]*>/gim, '')

            // Clean up excessive whitespace
            .replace(/\n{3,}/gim, '\n\n')
            .replace(/^\n+|\n+$/gim, '')
            .trim();
    }

    /**
     * Convert markdown to HTML
     * @param {string} markdown - The markdown text to convert
     * @returns {string} - The HTML representation
     */
    markdownToHTML(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/\[([^\]]+)\]\(([^\)]+)\)/gim, '<a href="$2">$1</a>')
            .replace(/!\[([^\]]*)\]\(([^\)]+)\)/gim, '<img alt="$1" src="$2" />')
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            .replace(/(\n<li>.*<\/li>\n)/gims, '<ul>$1</ul>')
            .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
            .replace(/(\n<li>.*<\/li>\n)/gims, '<ol>$1</ol>')
            .replace(/\n\n/gim, '</p><p>')
            .replace(/^(.*)$/gim, '<p>$1</p>')
            .replace(/<p><\/p>/gim, '')
            .replace(/<p>(<h[1-6]>.*<\/h[1-6]>)<\/p>/gim, '$1')
            .replace(/<p>(<ul>.*<\/ul>)<\/p>/gims, '$1')
            .replace(/<p>(<ol>.*<\/ol>)<\/p>/gims, '$1');
    }

    /**
     * Create inline markdown editor
     * @param {Element} element - The editable element
     */
    async createMarkdownEditModal(element) {
        // Get the current markdown content
        const editButton = element.querySelector('.component-edit-button');
        element.removeChild(editButton);
        const existingHTML = element.innerHTML;
        const existingMarkdown = element.dataset.markdown || this.htmlToMarkdown(existingHTML);
        element.appendChild(editButton);
        console.log("md length " + existingMarkdown.length);

        // Store original content and hide edit button
        const originalContent = element.innerHTML;
        editButton.style.display = 'none';

        // Create container for EasyMDE
        const editorContainer = document.createElement('div');
        editorContainer.style.cssText = `
            width: 100%;
            min-height: 400px;
            border: 2px solid #007bff;
            border-radius: 4px;
            position: relative;
        `;

        // Create unique ID for this editor instance
        const editorId = 'markdown-editor-' + Date.now();
        editorContainer.id = editorId;

        // Create editor content structure
        editorContainer.innerHTML = `
            <textarea style="display: none;">${existingMarkdown}</textarea>
        `;

        // Create submit/cancel buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            margin-top: 10px;
            text-align: right;
        `;
        buttonContainer.innerHTML = `
            <button id="submit-btn" style="padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Submit</button>
            <button id="cancel-btn" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
        `;

        // Replace element content with editor
        element.innerHTML = '';
        element.appendChild(editorContainer);
        element.appendChild(buttonContainer);

        // Show loading indicator
        editorContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 400px; font-size: 16px; color: #666;">
                Loading EasyMDE...
            </div>
        `;

        // Initialize EasyMDE variable in outer scope
        let editorInstance = null;

        try {
            console.log("Testing");
            // Load EasyMDE if not already loaded
            await this.loadEasyMDE();

            // Create textarea element
            const textarea = document.createElement('textarea');
            textarea.id = editorId;
            textarea.value = existingMarkdown;

            console.log("textarea value " + textarea.value);

            // Clear container and add textarea
            editorContainer.innerHTML = '';
            editorContainer.appendChild(textarea);

            // Wait a moment for DOM to settle, then initialize EasyMDE
            setTimeout(() => {
                console.log('Initializing EasyMDE with ID:', editorId);
                console.log('EasyMDE available:', typeof EasyMDE);
                console.log('EasyMDE constructor:', EasyMDE);

                try {
                    console.log("textarea value " + textarea.value);
                    if (!textarea) {
                        throw new Error('Textarea element not found in DOM');
                    }

                    console.log('Textarea element found:', textarea);
                    console.log('Creating EasyMDE instance...');

                    // Try the most minimal configuration first
                    editorInstance = new EasyMDE({
                        element: textarea,
                        minHeight: "200px",
                        toolbar: [
                            "bold", "italic", "strikethrough", "heading-1", "heading-2", "heading-3", "|", "quote", "unordered-list", "ordered-list", "code", "|", "link", "table", "upload-image", "|", "side-by-side", "|", "undo", "redo", "|", "guide"
                        ]
                    });
                    console.log('EasyMDE instance created:', editorInstance);
                } catch (initError) {
                    console.error('Error initializing EasyMDE:', initError);
                    // Fall back to simple textarea
                    editorContainer.innerHTML = `
                        <textarea id="fallback-editor" style="width: 100%; height: 400px; padding: 10px; border: 1px solid #ddd; resize: vertical; font-family: monospace;">${existingMarkdown}</textarea>
                    `;
                }
            }, 100);
        } catch (error) {
            console.error('Failed to load EasyMDE, falling back to simple textarea:', error);
            editorContainer.innerHTML = `
                <textarea id="fallback-editor" style="width: 100%; height: 400px; padding: 10px; border: none; resize: vertical; font-family: monospace;">${existingMarkdown}</textarea>
            `;
        }

        const saveChanges = () => {
            let newMarkdown;
            let newHTML;

            if (editorInstance) {
                newMarkdown = editorInstance.value();
                // EasyMDE doesn't have getHTML, so we'll convert markdown to HTML manually
                newHTML = this.markdownToHTML(newMarkdown);
            } else {
                // Fallback for when EasyMDE is not available
                const fallbackEditor = editorContainer.querySelector('#fallback-editor');
                newMarkdown = fallbackEditor ? fallbackEditor.value : existingMarkdown;
                // Simple markdown to HTML conversion
                newHTML = newMarkdown
                    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                    .replace(/\*(.*)\*/gim, '<em>$1</em>')
                    .replace(/\n/gim, '<br>');
            }

            // Restore original structure with updated content
            element.innerHTML = originalContent;
            const editButton = element.querySelector('.component-edit-button');

            // Update the element's content and data
            element.dataset.markdown = newMarkdown;

            // Update innerHTML while preserving the edit button
            element.childNodes.forEach(node => {
                if (node !== editButton && (node.nodeType === Node.TEXT_NODE || (node.nodeType === Node.ELEMENT_NODE && !node.classList.contains('component-edit-button')))) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.remove();
                    } else {
                        node.innerHTML = newHTML;
                    }
                }
            });

            // If no content nodes exist, create a new one
            if (!element.innerHTML.includes(newHTML) && newHTML !== originalContent) {
                const contentDiv = document.createElement('div');
                contentDiv.innerHTML = newHTML;
                element.insertBefore(contentDiv, editButton);
            }

            editButton.style.display = '';
            setTimeout(() => this.savePage(), 100);
        };

        const cancelEdit = () => {
            element.innerHTML = originalContent;
            const editButton = element.querySelector('.component-edit-button');
            editButton.style.display = '';
        };

        // Handle submit button
        buttonContainer.querySelector('#submit-btn').addEventListener('click', (e) => {
            e.preventDefault();
            saveChanges();
        });

        // Handle cancel button
        buttonContainer.querySelector('#cancel-btn').addEventListener('click', (e) => {
            e.preventDefault();
            cancelEdit();
        });

        // Return null since we're not creating a modal
        return null;
    }

    /**
     * Insert component into the target element
     * @param {Object} component - The component to insert
     * @param {Object} params - Parameter values (unused since components no longer have parameters)
     * @param {Element} targetElement - The target DOM element
     */
    insertComponent(component, params, targetElement) {
        try {
            // Process component content
            let processedContent = component.content;

            // Remove comment lines with @target and @param
            processedContent = processedContent.replace(/<!--\s*@(target|param).*?-->/g, '');

            // Create temporary container to parse HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = processedContent.trim();

            // Insert the processed content
            if (component.target.includes(':child')) {
                // Insert as child
                while (tempDiv.firstChild) {
                    targetElement.appendChild(tempDiv.firstChild);
                }
            } else {
                // Insert before the element
                while (tempDiv.firstChild) {
                    targetElement.parentNode.insertBefore(tempDiv.firstChild, targetElement);
                }
            }

            console.log(`Inserted component ${component.name}`);

            // Refresh insertion buttons to account for new DOM structure
            setTimeout(() => this.savePage(), 100);

        } catch (error) {
            console.error('Failed to insert component:', error);
            alert('Failed to insert component: ' + error.message);
        }
    }

    async getPageContent() {
        try {
            // Send the HTML to the backend to save
            const response = await fetch(`http://127.0.0.1:8000/api/v1/sites/${this.siteId}/pages/${this.pageId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to get page: ${response.statusText}`);
            }

            const pageContent = await response.text();
            return pageContent;
        } catch (error) {
            console.error('Failed to add to head and save:', error);
            throw error;
        }
    }

    /**
     * Save page to disk
     */
    async savePage() {
        try {
            this.removeInsertionButtons();
            // Send the HTML to the backend to save
            const response = await fetch(`http://127.0.0.1:8000/api/v1/sites/${this.siteId}/pages/${this.pageId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: document.documentElement.outerHTML
                })
            });

            if (response.ok) {
                // Reload the page
                window.location.reload();
            } else {
                throw new Error(`Failed to save page: ${response.statusText}`);
            }


        } catch (error) {
            console.error('Failed to add to head and save:', error);
            throw error;
        }
    }

    /**
     * Refresh the UI (reload components and re-inject buttons)
     */
    async refresh() {
        await this.init();
    }
}

// Global instance
window.siteModificationUI = new SiteModificationUI();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.siteModificationUI.init();
    });
} else {
    window.siteModificationUI.init();
}