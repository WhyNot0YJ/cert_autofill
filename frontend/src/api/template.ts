import api from './index'
import type { 
  ApiResponse, 
  BaseQueryParams 
} from '../types/api'

// 模板相关类型定义
export interface Template {
  id: number
  template_name: string
  display_name: string
  description?: string
  category: string
  version: string
  variables: string[]
  source_template?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateTemplateRequest {
  template_name: string
  display_name: string
  description?: string
  category: string
  selected_variables: string[]
  source_template?: string
}

export interface UpdateTemplateRequest {
  display_name?: string
  description?: string
  variables?: string[]
  is_active?: boolean
}

export interface TemplateListParams extends BaseQueryParams {
  category?: string
  is_active?: boolean
}

export interface TemplateVariable {
  name: string
  display_name: string
  description?: string
  type: 'string' | 'number' | 'boolean' | 'date' | 'array'
  required: boolean
  default_value?: any
  validation_rules?: string[]
}

export interface TemplateListResponse {
  success: boolean
  data: {
    templates: Template[]
    pagination: {
      page: number
      per_page: number
      total: number
      pages: number
    }
    categories: string[]
    filters: {
      category: string[]
      is_active: boolean[]
    }
  }
}

// 模板API类
class TemplateAPI {
  private readonly basePath = '/template'

  /**
   * 获取所有模板
   */
  async getTemplates(params?: TemplateListParams): Promise<TemplateListResponse> {
    const queryParams = new URLSearchParams()
    
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order)
    if (params?.category) queryParams.append('category', params.category)
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
    
    const url = `${this.basePath}/templates${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return api.get(url)
  }

  /**
   * 获取可用变量
   */
  async getVariables(): Promise<ApiResponse<TemplateVariable[]>> {
    return api.get(`${this.basePath}/templates/variables`)
  }

  /**
   * 创建新模板
   */
  async createTemplate(data: CreateTemplateRequest): Promise<ApiResponse<Template>> {
    return api.post(`${this.basePath}/templates`, data)
  }

  /**
   * 获取模板配置
   */
  async getTemplateConfig(templateName: string): Promise<ApiResponse<Template>> {
    return api.get(`${this.basePath}/templates/${templateName}`)
  }

  /**
   * 更新模板
   */
  async updateTemplate(templateName: string, data: UpdateTemplateRequest): Promise<ApiResponse<Template>> {
    return api.put(`${this.basePath}/templates/${templateName}`, data)
  }

  /**
   * 删除模板
   */
  async deleteTemplate(templateName: string): Promise<ApiResponse<void>> {
    return api.delete(`${this.basePath}/templates/${templateName}`)
  }

  /**
   * 下载模板
   */
  async downloadTemplate(templateName: string): Promise<Blob> {
    return api.get(`${this.basePath}/templates/${templateName}/download`, {
      responseType: 'blob'
    })
  }

  /**
   * 复制模板
   */
  async copyTemplate(templateName: string, newName: string): Promise<ApiResponse<Template>> {
    return api.post(`${this.basePath}/templates/${templateName}/copy`, {
      new_name: newName
    })
  }

  /**
   * 激活/停用模板
   */
  async toggleTemplateStatus(templateName: string, isActive: boolean): Promise<ApiResponse<Template>> {
    return api.patch(`${this.basePath}/templates/${templateName}/status`, {
      is_active: isActive
    })
  }

  /**
   * 获取模板预览
   */
  async getTemplatePreview(templateName: string, sampleData?: any): Promise<ApiResponse<{
    preview_url: string
    variables_used: string[]
    missing_variables: string[]
  }>> {
    return api.post(`${this.basePath}/templates/${templateName}/preview`, {
      sample_data: sampleData
    })
  }

  /**
   * 获取模板统计信息
   */
  async getTemplateStats(): Promise<ApiResponse<{
    total_templates: number
    active_templates: number
    categories_count: number
    most_used_template: string
    recently_updated: Template[]
  }>> {
    return api.get(`${this.basePath}/templates/stats`)
  }

  /**
   * 批量操作模板
   */
  async batchUpdateTemplates(templateNames: string[], data: Partial<UpdateTemplateRequest>): Promise<ApiResponse<{ updated_count: number }>> {
    return api.put(`${this.basePath}/templates/batch-update`, {
      template_names: templateNames,
      data
    })
  }

  /**
   * 导出模板配置
   */
  async exportTemplateConfig(templateName: string): Promise<Blob> {
    return api.get(`${this.basePath}/templates/${templateName}/export`, {
      responseType: 'blob'
    })
  }

  /**
   * 导入模板配置
   */
  async importTemplateConfig(configFile: File): Promise<ApiResponse<Template>> {
    const formData = new FormData()
    formData.append('config_file', configFile)
    
    return api.post(`${this.basePath}/templates/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 导出单例实例
export const templateAPI = new TemplateAPI() 