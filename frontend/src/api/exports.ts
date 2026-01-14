// 统一导出所有API模块
export { companyAPI } from './company'
export { applicationAPI } from './application'
export { mvpAPI } from './mvp'
export { uploadAPI } from './upload'

// 导出类型定义
export type {
  Company,
  CreateCompanyRequest,
  UpdateCompanyRequest,
  CompanyListParams,
  CompanyListResponse
} from './company'

export type {
  Application,
  ApplicationListParams,
  CreateApplicationRequest,
  UpdateApplicationRequest,
  ApplicationListResponse
} from './application'




export type {
  UploadOptions,
  UploadProgressCallback,
  UploadErrorCallback
} from './upload'

// 导出通用类型
export type {
  ApiResponse,
  ApiError,
  ErrorCode,
  BaseQueryParams,
  PaginationInfo,
  ListResponse,
  FileUploadResponse,
  extractionResult,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
  SessionInfo
} from '../types/api'
