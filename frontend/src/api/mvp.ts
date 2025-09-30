import api from './index'
import type { 
  ApiResponse, 
  AIExtractionResult,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
  SessionInfo,
} from '../types/api'

// MVP相关类型定义
export interface MVPFormData {
  session_id: string
  form_data: Record<string, any>
  metadata?: {
    source_documents: string[]
    extraction_method: 'ai' | 'manual'
    last_updated: string
  }
}

export interface DocumentUploadRequest {
  session_id: string
  documents: File[]
  document_types: string[]
}

export interface DocumentUploadResponse {
  success: boolean
  message: string
  data: {
    uploaded_files: string[]
    session_id: string
    processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  }
}

export interface AIExtractionRequest {
  session_id: string
  extraction_options?: {
    language?: 'zh' | 'en'
    confidence_threshold?: number
    extract_fields?: string[]
  }
}

export interface AIExtractionResponse {
  success: boolean
  message: string
  data: {
    extraction_result: AIExtractionResult
    confidence_scores: Record<string, number>
    extraction_time: number
    fields_extracted: string[]
  }
}

export interface FormDataSaveRequest {
  session_id: string
  form_data: Record<string, any>
  save_type: 'draft' | 'final'
  version?: string
}

export interface FormDataResponse {
  success: boolean
  message: string
  data: {
    form_data: Record<string, any>
    saved_at: string
    version: string
    session_info: SessionInfo
  }
}

// MVP API类
class MVPAPI {
  private readonly basePath = '/mvp'

  /**
   * 上传申请书和检测报告
   */
  async uploadDocuments(
    formData: FormData,
    onProgress?: (progress: number) => void,
    onError?: (error: any) => void
  ): Promise<DocumentUploadResponse> {
    try {
      const response = await api.post(`${this.basePath}/upload-documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
      
      // 拦截器已经返回了业务数据，直接返回
      return response as unknown as DocumentUploadResponse
    } catch (error) {
      if (onError) {
        onError(error)
      }
      throw error
    }
  }

  /**
   * 使用文档提取功能
   */
  async extractInfo(data: AIExtractionRequest): Promise<AIExtractionResponse> {
    return api.post(`${this.basePath}/extract-info`, data)
  }

  /**
   * 保存表单数据
   */
  async saveFormData(data: FormDataSaveRequest): Promise<ApiResponse<{ saved_at: string; version: string; session_id: string }>> {
    return api.post(`${this.basePath}/save-form-data`, data)
  }

  /**
   * 获取表单数据
   */
  async getFormData(sessionId: string): Promise<FormDataResponse> {
    return api.get(`${this.basePath}/get-form-data/${sessionId}`)
  }

  /**
   * 生成IF文档
   */
  async generateIF(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-if`, data)
  }

  /**
   * 生成所有文档
   */
  async generateDocuments(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-documents`, data)
  }

  /**
   * 生成CERT文档
   */
  async generateCert(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-cert`, data)
  }

  /**
   * 生成OTHER文档
   */
  async generateOther(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-other`, data)
  }

  /**
   * 生成TR文档
   */
  async generateTR(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-tr`, data)
  }

  /**
   * 生成Review Control Sheet
   */
  async generateReviewControlSheet(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-review-control-sheet`, data)
  }

  /**
   * 生成TM文档
   */
  async generateTM(data: DocumentGenerationRequest): Promise<DocumentGenerationResponse> {
    return api.post(`${this.basePath}/generate-tm`, data)
  }


  /**
   * 下载生成的文档
   */
  async downloadDocument(filename: string): Promise<Blob> {
    return api.get(`${this.basePath}/download/${filename}`, {
      responseType: 'blob',
    })
  }

  /**
   * 获取会话信息
   */
  async getSessionInfo(sessionId: string): Promise<ApiResponse<SessionInfo>> {
    return api.get(`${this.basePath}/session/${sessionId}`)
  }

  /**
   * 创建新会话
   */
  async createSession(metadata?: { project_name?: string; description?: string }): Promise<ApiResponse<{ session_id: string }>> {
    return api.post(`${this.basePath}/session`, metadata)
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId: string): Promise<ApiResponse<void>> {
    return api.delete(`${this.basePath}/session/${sessionId}`)
  }

  /**
   * 获取会话列表
   */
  async getSessions(params: {
    page?: number
    per_page?: number
    status?: string
    search?: string
  } = {}): Promise<ApiResponse<{
    sessions: SessionInfo[]
    pagination: {
      page: number
      per_page: number
      total: number
      pages: number
    }
  }>> {
    const queryParams = new URLSearchParams()
    
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params.status) queryParams.append('status', params.status)
    if (params.search) queryParams.append('search', params.search)
    
    const url = `${this.basePath}/sessions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return api.get(url)
  }

  /**
   * 验证表单数据
   */
  async validateFormData(sessionId: string, formData: Record<string, any>): Promise<ApiResponse<{
    valid: boolean
    errors: Array<{ field: string; message: string; code: string }>
    warnings: Array<{ field: string; message: string; code: string }>
  }>> {
    return api.post(`${this.basePath}/validate-form-data`, {
      session_id: sessionId,
      form_data: formData
    })
  }

  /**
   * 获取生成进度
   */
  async getGenerationProgress(sessionId: string): Promise<ApiResponse<{
    status: 'pending' | 'processing' | 'completed' | 'failed'
    progress: number
    current_step: string
    estimated_time?: number
    error_message?: string
  }>> {
    return api.get(`${this.basePath}/generation-progress/${sessionId}`)
  }

  /**
   * 取消文档生成
   */
  async cancelGeneration(sessionId: string): Promise<ApiResponse<void>> {
    return api.post(`${this.basePath}/cancel-generation/${sessionId}`)
  }
  /**
 * AI文档信息提取
 */
  async aiExtract(file: File): Promise<ApiResponse<AIExtractionResult>> {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post(`${this.basePath}/document-extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  
  }
}

// 导出单例实例
export const mvpAPI = new MVPAPI()
export default mvpAPI 