import api from './index'
import type { 
  ApiResponse, 
  extractionResult,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
} from '../types/api'


// MVP API类
class MVPAPI {
  private readonly basePath = '/mvp'

  /**
   * 保存表单数据
   */
  async saveFormData(data: { session_id?: string; form_data: Record<string, any> }): Promise<ApiResponse<{ saved_at: string; version: string; session_id: string }>> {
    return api.post(`${this.basePath}/save-form-data`, data)
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
 * 文档信息提取
 */
  async documentExtraction(file: File): Promise<ApiResponse<extractionResult>> {
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