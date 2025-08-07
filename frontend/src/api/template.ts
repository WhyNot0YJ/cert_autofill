import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api/template'

export const templateAPI = {
  // 获取所有模板
  getTemplates() {
    return axios.get(`${API_BASE_URL}/templates`)
  },

  // 获取可用变量
  getVariables() {
    return axios.get(`${API_BASE_URL}/templates/variables`)
  },

  // 创建新模板
  createTemplate(data: {
    template_name: string
    selected_variables: string[]
    description?: string
    source_template?: string
  }) {
    return axios.post(`${API_BASE_URL}/templates`, data)
  },

  // 获取模板配置
  getTemplateConfig(templateName: string) {
    return axios.get(`${API_BASE_URL}/templates/${templateName}`)
  },

  // 删除模板
  deleteTemplate(templateName: string) {
    return axios.delete(`${API_BASE_URL}/templates/${templateName}`)
  },

  // 下载模板
  downloadTemplate(templateName: string) {
    return axios.get(`${API_BASE_URL}/templates/${templateName}/download`, {
      responseType: 'blob'
    })
  }
} 