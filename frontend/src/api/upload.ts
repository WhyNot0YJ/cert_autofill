import api from './index'
import type { 
  ApiResponse, 
  FileUploadResponse 
} from '../types/api'

// 上传选项类型
export interface UploadOptions {
  category?: string    // 文件分类 (company/document/temp等)
  subcategory?: string // 子分类 (marks/picture/signature等)
  description?: string // 文件描述
  tags?: string[]      // 文件标签
}

export interface UploadProgressCallback {
  (progress: number): void
}

export interface UploadErrorCallback {
  (error: any): void
}

// 文件上传API类
class UploadAPI {
  private readonly basePath = '/mvp/upload-file'

  /**
   * 通用文件上传
   */
  async uploadFile(
    file: File, 
    options: UploadOptions = {},
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    // 添加分类参数
    if (options.category) {
      formData.append('category', options.category)
    }
    if (options.subcategory) {
      formData.append('subcategory', options.subcategory)
    }
    if (options.description) {
      formData.append('description', options.description)
    }
    if (options.tags && options.tags.length > 0) {
      options.tags.forEach(tag => formData.append('tags[]', tag))
    }
    
    try {
      const response = await api.post(this.basePath, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
      
      return response
    } catch (error) {
      if (onError) {
        onError(error)
      }
      throw error
    }
  }

  /**
   * 上传商标图片
   */
  async uploadTradeMarkImage(
    file: File,
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse> {
    return this.uploadFile(file, {
      category: 'company',
      subcategory: 'marks'
    }, onProgress, onError)
  }

  /**
   * 上传公司图片
   */
  async uploadCompanyPicture(
    file: File,
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse> {
    return this.uploadFile(file, {
      category: 'company',
      subcategory: 'picture'
    }, onProgress, onError)
  }

  /**
   * 上传签名图片
   */
  async uploadCompanySignature(
    file: File,
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse> {
    return this.uploadFile(file, {
      category: 'company',
      subcategory: 'signature'
    }, onProgress, onError)
  }

  /**
   * 上传文档文件
   */
  async uploadDocument(
    file: File,
    documentType: string,
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse> {
    return this.uploadFile(file, {
      category: 'document',
      subcategory: documentType
    }, onProgress, onError)
  }

  /**
   * 批量上传文件
   */
  async uploadMultipleFiles(
    files: File[],
    options: UploadOptions = {},
    onProgress?: UploadProgressCallback,
    onError?: UploadErrorCallback
  ): Promise<FileUploadResponse[]> {
    const uploadPromises = files.map(file => 
      this.uploadFile(file, options, onProgress, onError)
    )
    
    return Promise.all(uploadPromises)
  }

  /**
   * 删除已上传的文件
   */
  async deleteFile(filename: string): Promise<ApiResponse<void>> {
    return api.delete(`${this.basePath}/${filename}`)
  }

  /**
   * 获取文件信息
   */
  async getFileInfo(filename: string): Promise<ApiResponse<{
    filename: string
    original_name: string
    size: number
    mime_type: string
    category: string
    subcategory: string
    uploaded_at: string
    url: string
  }>> {
    return api.get(`${this.basePath}/${filename}/info`)
  }

  /**
   * 获取上传历史
   */
  async getUploadHistory(params: {
    category?: string
    subcategory?: string
    page?: number
    per_page?: number
  } = {}): Promise<ApiResponse<{
    files: any[]
    pagination: {
      page: number
      per_page: number
      total: number
      pages: number
    }
  }>> {
    const queryParams = new URLSearchParams()
    
    if (params.category) queryParams.append('category', params.category)
    if (params.subcategory) queryParams.append('subcategory', params.subcategory)
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.per_page) queryParams.append('per_page', params.per_page.toString())
    
    const url = `${this.basePath}/history${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return api.get(url)
  }
}

// 导出单例实例
export const uploadAPI = new UploadAPI()
