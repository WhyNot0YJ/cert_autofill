import api from './index'
import type { 
  ApiResponse, 
  BaseQueryParams, 
  PaginationInfo 
} from '../types/api'

// 公司相关类型定义
export interface Company {
  id: number
  name: string
  address?: string
  signature?: string
  picture?: string
  trade_names?: string[]
  trade_marks?: string[]
  created_at?: string
  updated_at?: string
}

export interface CreateCompanyRequest {
  name: string
  address?: string
  signature?: File
  picture?: File
  trade_names?: string[]
  trade_marks?: string[]
}

export interface UpdateCompanyRequest {
  name?: string
  address?: string
  signature?: File
  picture?: File
  trade_names?: string[]
  trade_marks?: string[]
}

export interface CompanyListParams extends BaseQueryParams {
  // 继承基础查询参数
}

export interface CompanyListResponse {
  success: boolean
  data: {
    companies: Company[]
    pagination: PaginationInfo
    search: string
    sort: {
      sort_by: string
      sort_order: string
    }
  }
}

// 公司API类
class CompanyAPI {
  private readonly basePath = '/companies'

  /**
   * 获取公司列表 - 支持分页和搜索
   */
  async getCompanies(params?: CompanyListParams): Promise<CompanyListResponse> {
    const queryParams = new URLSearchParams()
    
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order)
    
    const url = queryParams.toString() ? `${this.basePath}?${queryParams.toString()}` : this.basePath
    return api.get(url)
  }

  /**
   * 获取所有公司（简单版本，用于下拉框等）
   */
  async getAllCompanies(): Promise<CompanyListResponse> {
    return api.get(`${this.basePath}?per_page=1000`)
  }

  /**
   * 获取单个公司
   */
  async getCompany(id: number): Promise<ApiResponse<Company>> {
    return api.get(`${this.basePath}/${id}`)
  }

  /**
   * 创建公司
   */
  async createCompany(data: CreateCompanyRequest): Promise<ApiResponse<Company>> {
    const requestData = {
      name: data.name,
      address: data.address,
      trade_names: data.trade_names || [],
      trade_marks: data.trade_marks || []
    }
    
    // TODO: 暂时不支持文件上传，仅处理基本字段
    // if (data.signature) requestData.signature = data.signature
    // if (data.picture) requestData.picture = data.picture
    
    return api.post(this.basePath, requestData)
  }

  /**
   * 更新公司
   */
  async updateCompany(id: number, data: UpdateCompanyRequest): Promise<ApiResponse<Company>> {
    const requestData: any = {}
    
    if (data.name !== undefined) requestData.name = data.name
    if (data.address !== undefined) requestData.address = data.address
    if (data.trade_names !== undefined) requestData.trade_names = data.trade_names || []
    if (data.trade_marks !== undefined) requestData.trade_marks = data.trade_marks || []
    
    // TODO: 暂时不支持文件上传，仅处理基本字段
    // if (data.signature) requestData.signature = data.signature
    // if (data.picture) requestData.picture = data.picture
    
    return api.put(`${this.basePath}/${id}`, requestData)
  }

  /**
   * 删除公司
   */
  async deleteCompany(id: number): Promise<ApiResponse<void>> {
    return api.delete(`${this.basePath}/${id}`)
  }

  /**
   * 上传公司图片
   */
  async uploadCompanyPicture(id: number, file: File): Promise<ApiResponse<Company>> {
    const formData = new FormData()
    formData.append('picture', file)
    
    return api.put(`${this.basePath}/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  /**
   * 上传公司签名
   */
  async uploadCompanySignature(id: number, file: File): Promise<ApiResponse<Company>> {
    const formData = new FormData()
    formData.append('signature', file)
    
    return api.put(`${this.basePath}/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  /**
   * 批量操作
   */
  async batchDelete(ids: number[]): Promise<ApiResponse<{ deleted_count: number }>> {
    return api.post(`${this.basePath}/batch-delete`, { ids })
  }

  /**
   * 导出公司数据
   */
  async exportCompanies(params?: CompanyListParams): Promise<Blob> {
    const queryParams = new URLSearchParams()
    
    if (params?.search) queryParams.append('search', params.search)
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order)
    
    const url = `${this.basePath}/export${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    
    return api.get(url, {
      responseType: 'blob'
    })
  }
}

// 导出单例实例
export const companyAPI = new CompanyAPI()
