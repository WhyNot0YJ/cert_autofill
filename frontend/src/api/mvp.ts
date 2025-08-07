import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/mvp',
  timeout: 30000, // 增加超时时间，因为AI处理可能需要较长时间
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('MVP API Error:', error);
    return Promise.reject(error);
  }
);

// MVP相关API
export const mvpAPI = {
  // 上传申请书和检测报告
  uploadDocuments: (formData: FormData) => 
    api.post('/upload-documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // 使用AI提取文档信息
  extractInfo: (data: { session_id: string }) => 
    api.post('/extract-info', data),

  // 保存表单数据
  saveFormData: (data: { session_id: string; form_data: any }) => 
    api.post('/save-form-data', data),

  // 获取表单数据
  getFormData: (sessionId: string) => 
    api.get(`/get-form-data/${sessionId}`),

  // 生成交付文档
  generateDocuments: (data: { session_id: string; output_format?: string }) => 
    api.post('/generate-documents', data),

  // 下载生成的文档
  downloadDocument: (filename: string) => 
    api.get(`/download/${filename}`, {
      responseType: 'blob',
    }),
};

export default mvpAPI; 