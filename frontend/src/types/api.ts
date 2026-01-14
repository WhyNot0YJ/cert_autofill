// API 响应和错误的类型定义

// 标准API响应格式
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
}

// 标准API错误格式
export interface ApiError {
  message: string
  code: string
  originalError?: any
  status?: number
  data?: any
}

// HTTP状态码对应的错误类型
export type HttpErrorCode = 
  | 'BAD_REQUEST'           // 400
  | 'UNAUTHORIZED'          // 401
  | 'FORBIDDEN'            // 403
  | 'NOT_FOUND'            // 404
  | 'VALIDATION_ERROR'     // 422
  | 'SERVER_ERROR'         // 500
  | 'BAD_GATEWAY'          // 502
  | 'SERVICE_UNAVAILABLE'  // 503
  | 'NETWORK_ERROR'        // 网络错误
  | 'NO_RESPONSE'          // 无响应
  | 'REQUEST_ERROR'        // 请求配置错误

// 业务错误码
export type BusinessErrorCode = 
  | 'COMPANY_NOT_FOUND'
  | 'COMPANY_ALREADY_EXISTS'
  | 'INVALID_COMPANY_DATA'
  | 'FILE_UPLOAD_FAILED'
  | 'PERMISSION_DENIED'
  | 'RATE_LIMIT_EXCEEDED'
  | 'AI_EXTRACTION_FAILED'
  | 'DOCUMENT_GENERATION_FAILED'
  | 'TEMPLATE_NOT_FOUND'
  | 'SESSION_EXPIRED'

// 完整的错误码类型
export type ErrorCode = HttpErrorCode | BusinessErrorCode

// 分页信息
export interface PaginationInfo {
  page: number
  per_page: number
  total: number
  pages: number
  has_prev: boolean
  has_next: boolean
  prev_num: number | null
  next_num: number | null
}

// 列表响应格式
export interface ListResponse<T> {
  success: boolean
  data: {
    items: T[]
    pagination: PaginationInfo
    search?: string
    sort?: {
      sort_by: string
      sort_order: string
    }
  }
}

// 通用查询参数
export interface BaseQueryParams {
  page?: number
  per_page?: number
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

// 文件上传响应
export interface FileUploadResponse {
  success: boolean
  message: string
  data: {
    url: string
    filename: string
    original_name: string
    category: string
    subcategory: string
    size: number
    mime_type: string
  }
}

// 提取结果
export interface extractionResult {
  enterprise_info: {
    name: string
    english_name?: string
    address: string
  }
  certification_info: {
    type: string
    product_name: string
  }
  technical_specs: {
    windscreen_thickness: string
    interlayer_thickness: string
    glass_layers: string
    interlayer_layers: string
    interlayer_type: string
    glass_treatment: string
    coating_type: string
    coating_thickness: string
    coating_color: string
    material_nature: string[]
    glass_coloring: string[]
    conductors: string[]
    obscuration_bands: string[]
  }
  vehicle_info: any[]
  trade_names: string[]
  interlayer_coloring: string[]
}

// 文档生成请求
export interface DocumentGenerationRequest {
  session_id: string
  output_format?: 'docx' | 'pdf' | 'xlsx'
  template_name?: string
}

// 文档生成响应
export interface DocumentGenerationResponse {
  success: boolean
  message: string
  data: {
    download_url: string
    filename: string
    file_size: number
    generated_at: string
  }
}

// 会话管理
export interface SessionInfo {
  session_id: string
  created_at: string
  last_activity: string
  status: 'active' | 'expired' | 'completed'
  documents_count: number
}
