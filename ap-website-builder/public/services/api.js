const API_BASE = 'http://127.0.0.1:8000/api/v1';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Site Management
  async getSites() {
    return this.request('/sites');
  }

  async createSite(data) {
    return this.request('/sites', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSite(siteId) {
    return this.request(`/sites/${siteId}`);
  }

  async updateSite(siteId, data) {
    return this.request(`/sites/${siteId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteSite(siteId) {
    return this.request(`/sites/${siteId}`, {
      method: 'DELETE',
    });
  }

  // Page Management
  async getPages(siteId) {
    return this.request(`/sites/${siteId}/pages`);
  }

  async getPage(siteId, pageId) {
    return this.request(`/sites/${siteId}/pages/${pageId}`);
  }

  async createPage(siteId, data) {
    return this.request(`/sites/${siteId}/pages`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePage(siteId, pageId, data) {
    return this.request(`/sites/${siteId}/pages/${pageId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePage(siteId, pageId) {
    return this.request(`/sites/${siteId}/pages/${pageId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiService();