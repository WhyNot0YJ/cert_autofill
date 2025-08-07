import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
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
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 企业相关API
export const enterpriseAPI = {
  // 获取企业列表
  getEnterprises: (params?: any) => api.get('/enterprises', { params }),
  
  // 创建企业
  createEnterprise: (data: any) => api.post('/enterprises', data),
  
  // 获取企业详情
  getEnterprise: (id: number) => api.get(`/enterprises/${id}`),
  
  // 更新企业
  updateEnterprise: (id: number, data: any) => api.put(`/enterprises/${id}`, data),
  
  // 删除企业
  deleteEnterprise: (id: number) => api.delete(`/enterprises/${id}`),
  
  // 获取模拟企业数据
  getMockEnterprises: () => api.get('/mock/enterprises'),
};

// 申请书相关API
export const applicationAPI = {
  // 获取申请书列表
  getApplications: (params?: any) => api.get('/applications', { params }),
  
  // 创建申请书
  createApplication: (data: any) => api.post('/applications', data),
  
  // 获取申请书详情
  getApplication: (id: number) => api.get(`/applications/${id}`),
  
  // 更新申请书
  updateApplication: (id: number, data: any) => api.put(`/applications/${id}`, data),
  
  // 删除申请书
  deleteApplication: (id: number) => api.delete(`/applications/${id}`),
  
  // 上传申请书文件
  uploadApplicationFile: (id: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/applications/${id}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 获取模拟申请书数据
  getMockApplications: () => api.get('/mock/applications'),
};

// 证书相关API
export const certificateAPI = {
  // 获取证书列表
  getCertificates: (params?: any) => api.get('/certificates', { params }),
  
  // 生成证书
  generateCertificate: (data: any) => api.post('/certificates/generate', data),
  
  // 获取证书详情
  getCertificate: (id: number) => api.get(`/certificates/${id}`),
  
  // 更新证书
  updateCertificate: (id: number, data: any) => api.put(`/certificates/${id}`, data),
  
  // 删除证书
  deleteCertificate: (id: number) => api.delete(`/certificates/${id}`),
  
  // 获取模拟证书数据
  getMockCertificates: () => api.get('/mock/certificates'),
};

// 报告相关API
export const reportAPI = {
  // 获取报告列表
  getReports: (params?: any) => api.get('/reports', { params }),
  
  // 创建报告
  createReport: (data: any) => api.post('/reports', data),
  
  // 获取报告详情
  getReport: (id: number) => api.get(`/reports/${id}`),
  
  // 更新报告
  updateReport: (id: number, data: any) => api.put(`/reports/${id}`, data),
  
  // 删除报告
  deleteReport: (id: number) => api.delete(`/reports/${id}`),
};

// 文件相关API
export const fileAPI = {
  // 下载文件
  downloadFile: (filename: string) => api.get(`/download/${filename}`, {
    responseType: 'blob',
  }),
};

// 系统相关API
export const systemAPI = {
  // 健康检查
  healthCheck: () => api.get('/health'),
};

// 保留原有的API函数以保持兼容性
export const extractFields = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/extract', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const generateDoc = (data: any) => api.post('/generate', data);

export default api;