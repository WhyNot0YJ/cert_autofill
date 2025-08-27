import api from './index'
import type { 
  ApiResponse, 
  BaseQueryParams, 
  PaginationInfo,
} from '../types/api'

// 申请书相关类型定义
export interface Application {
  id: number
  application_number: string
  title: string
  application_type: string
  status: string
  company_name?: string
  company_address?: string
  approval_no?: string
  information_folder_no?: string
  windscreen_thick?: string
  interlayer_thick?: string
  glass_layers?: string
  interlayer_layers?: string
  interlayer_type?: string
  glass_treatment?: string
  coating_type?: string
  coating_thick?: string
  coating_color?: string
  material_nature?: string
  safety_class?: string
  pane_desc?: string
  vehicles?: any[]
  remarks?: string
  created_at?: string
  updated_at?: string
  submitted_at?: string
  approved_at?: string
}

export interface ApplicationListParams extends BaseQueryParams {
  status?: string
  application_type?: string
  company_id?: number
}

export interface CreateApplicationRequest {
  title: string
  application_type: string
  company_id?: number
  company_name?: string
  company_address?: string
  approval_no?: string
  information_folder_no?: string
  windscreen_thick?: string
  interlayer_thick?: string
  glass_layers?: string
  interlayer_layers?: string
  interlayer_type?: string
  glass_treatment?: string
  coating_type?: string
  coating_thick?: string
  coating_color?: string
  material_nature?: string
  safety_class?: string
  pane_desc?: string
  vehicles?: any[]
  remarks?: string
}

export interface UpdateApplicationRequest extends Partial<CreateApplicationRequest> {
  status?: string
  submitted_at?: string
  approved_at?: string
}

export interface ApplicationListResponse {
  success: boolean
  data: {
    applications: Application[]
    pagination: PaginationInfo
    search: string
    filters: {
      status: string[]
      application_type: string[]
    }
    sort: {
      sort_by: string
      sort_order: string
    }
  }
}

// 申请书API类
class ApplicationAPI {
  private readonly basePath = '/applications'

  /**
   * 获取申请书列表
   */
  async getApplications(params: ApplicationListParams = {}): Promise<ApplicationListResponse> {
    const queryParams = new URLSearchParams()
    
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params.search) queryParams.append('search', params.search)
    if (params.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params.sort_order) queryParams.append('sort_order', params.sort_order)
    if (params.status) queryParams.append('status', params.status)
    if (params.application_type) queryParams.append('application_type', params.application_type)
    if (params.company_id) queryParams.append('company_id', params.company_id.toString())
    
    const url = queryParams.toString() ? `${this.basePath}?${queryParams.toString()}` : this.basePath
    return api.get(url)
  }

  /**
   * 获取单个申请书详情
   */
  async getApplication(id: number): Promise<ApiResponse<Application>> {
    return api.get(`${this.basePath}/${id}`)
  }

  /**
   * 创建申请书
   */
  async createApplication(data: CreateApplicationRequest): Promise<ApiResponse<Application>> {
    return api.post(this.basePath, data)
  }

  /**
   * 更新申请书
   */
  async updateApplication(id: number, data: UpdateApplicationRequest): Promise<ApiResponse<Application>> {
    return api.put(`${this.basePath}/${id}`, data)
  }

  /**
   * 删除申请书
   */
  async deleteApplication(id: number): Promise<ApiResponse<void>> {
    return api.delete(`${this.basePath}/${id}`)
  }

  /**
   * 提交申请书
   */
  async submitApplication(id: number): Promise<ApiResponse<Application>> {
    return api.post(`${this.basePath}/${id}/submit`)
  }

  /**
   * 审批申请书
   */
  async approveApplication(id: number, approvalData: { approved: boolean; remarks?: string }): Promise<ApiResponse<Application>> {
    return api.post(`${this.basePath}/${id}/approve`, approvalData)
  }

  /**
   * 获取申请书统计信息
   */
  async getApplicationStats(): Promise<ApiResponse<{
    total: number
    pending: number
    approved: number
    rejected: number
    draft: number
  }>> {
    return api.get(`${this.basePath}/stats`)
  }

  /**
   * 批量操作申请书
   */
  async batchUpdateApplications(ids: number[], data: Partial<UpdateApplicationRequest>): Promise<ApiResponse<{ updated_count: number }>> {
    return api.put(`${this.basePath}/batch-update`, { ids, data })
  }

  /**
   * 导出申请书数据
   */
  async exportApplications(params?: ApplicationListParams): Promise<Blob> {
    const queryParams = new URLSearchParams()
    
    if (params?.search) queryParams.append('search', params.search)
    if (params?.status) queryParams.append('status', params.status)
    if (params?.application_type) queryParams.append('application_type', params.application_type)
    if (params?.company_id) queryParams.append('company_id', params.company_id.toString())
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order)
    
    const url = `${this.basePath}/export${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    
    return api.get(url, {
      responseType: 'blob'
    })
  }
}

// 导出单例实例
export const applicationAPI = new ApplicationAPI()
