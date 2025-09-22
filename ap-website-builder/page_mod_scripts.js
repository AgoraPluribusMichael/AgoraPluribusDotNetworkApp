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
                button.style.cssText = `
                    position: absolute;
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    cursor: pointer;
                    z-index: 1000;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                `;

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
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        const modalContent = document.createElement('div');
        modalContent.classList.add('component-panel');

        modalContent.innerHTML = `
            <h3>Select Component to Insert</h3>
            <div class="component-list"></div>
            <button class="close-modal-btn" style="margin-top: 15px; padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
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
                this.showParameterInputModal(component, targetElement);
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
     * Show parameter input modal for selected component
     * @param {Object} component - The selected component
     * @param {Element} targetElement - The target DOM element
     */
    showParameterInputModal(component, targetElement) {
        const modal = this.createParameterInputModal(component, targetElement);
        document.body.appendChild(modal);
    }

    /**
     * Create parameter input modal
     */
    createParameterInputModal(component, targetElement) {
        const modal = document.createElement('div');
        modal.className = 'parameter-input-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        `;

        let formHTML = `
            <h3>Configure ${component.name}</h3>
            <form class="parameter-form">
        `;

        // Add input fields for each parameter
        component.params.forEach(param => {
            formHTML += `
                <div style="margin: 15px 0;">
                    <label for="param-${param}" style="display: block; margin-bottom: 5px; font-weight: bold;">${param}:</label>
                    <input type="text" id="param-${param}" name="${param}" 
                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"
                           placeholder="Enter value for ${param}">
                </div>
            `;
        });

        formHTML += `
                <div style="margin-top: 20px;">
                    <button type="submit" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px;">Insert Component</button>
                    <button type="button" class="cancel-btn" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
                </div>
            </form>
        `;

        modalContent.innerHTML = formHTML;

        // Handle form submission
        const form = modalContent.querySelector('.parameter-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const params = {};
            
            component.params.forEach(param => {
                params[param] = formData.get(param) || '';
            });

            modal.remove();
            this.insertComponent(component, params, targetElement);
        });

        // Cancel button
        const cancelBtn = modalContent.querySelector('.cancel-btn');
        cancelBtn.addEventListener('click', () => modal.remove());

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        modal.appendChild(modalContent);
        return modal;
    }

    /**
     * Insert component into the target element
     * @param {Object} component - The component to insert
     * @param {Object} params - Parameter values
     * @param {Element} targetElement - The target DOM element
     */
    insertComponent(component, params, targetElement) {
        try {
            // Process component content and replace parameters
            let processedContent = component.content;
            
            // Remove comment lines with @target and @param
            processedContent = processedContent.replace(/<!--\s*@(target|param).*?-->/g, '');
            
            // Replace parameter placeholders
            component.params.forEach(param => {
                const placeholder = `\${${param}}`;
                const value = params[param] || '';
                processedContent = processedContent.replace(new RegExp('\\$\\{' + param + '\\}', 'g'), value);
            });

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

            console.log(`Inserted component ${component.name} with params:`, params);
            
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
            window.alert(document.getElementsByClassName("component-insertion-button").length);
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