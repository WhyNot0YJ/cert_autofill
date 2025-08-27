// 统一导出所有API模块
export { companyAPI } from './company'
export { applicationAPI } from './application'
export { mvpAPI } from './mvp'
export { templateAPI } from './template'
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
  MVPFormData,
  DocumentUploadRequest,
  DocumentUploadResponse,
  AIExtractionRequest,
  AIExtractionResponse,
  FormDataSaveRequest,
  FormDataResponse
} from './mvp'

export type {
  Template,
  CreateTemplateRequest,
  UpdateTemplateRequest,
  TemplateListParams,
  TemplateVariable,
  TemplateListResponse
} from './template'

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
  AIExtractionResult,
  DocumentGenerationRequest,
  DocumentGenerationResponse,
  SessionInfo
} from '../types/api'
