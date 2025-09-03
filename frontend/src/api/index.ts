import axios from 'axios';
import type { ApiError, ErrorCode } from '../types/api';

// 获取后端端口配置
const getBackendPort = (): string => {
  // 优先使用环境变量中的端口
  if (import.meta.env.VITE_BACKEND_PORT) {
    return import.meta.env.VITE_BACKEND_PORT;
  }
  
  // 使用注入的全局变量
  if (typeof __BACKEND_PORT__ !== 'undefined') {
    return __BACKEND_PORT__;
  }
  
  // 默认端口 - 根据环境判断
  const isProduction = import.meta.env.PROD;
  return isProduction ? '5001' : '5000';
};

// 获取后端基础URL
const getBackendBaseURL = (): string => {
  const port = getBackendPort();
  
  // 优先使用环境变量中的服务器地址
  if (import.meta.env.VITE_SERVER_URL) {
    // 如果URL已经包含端口号，直接使用；否则添加端口号
    const baseUrl = import.meta.env.VITE_SERVER_URL;
    return baseUrl.includes(':') ? `${baseUrl}/api` : `${baseUrl}:${port}/api`;
  }
  
  // 使用注入的全局变量
  if (typeof __SERVER_URL__ !== 'undefined') {
    // 如果URL已经包含端口号，直接使用；否则添加端口号
    const baseUrl = __SERVER_URL__;
    return baseUrl.includes(':') ? `${baseUrl}/api` : `${baseUrl}:${port}/api`;
  }
  
  // 默认使用localhost
  return `http://localhost:${port}/api`;
};

// 创建axios实例
const api = axios.create({
  baseURL: getBackendBaseURL(),
  timeout: 120000,
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
    // 统一提取业务数据，直接返回 response.data
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    
    // 统一错误处理
    let errorMessage = '网络请求失败';
    let errorCode = 'NETWORK_ERROR';
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          errorMessage = data?.message || '请求参数错误';
          errorCode = 'BAD_REQUEST';
          break;
        case 401:
          errorMessage = '未授权，请重新登录';
          errorCode = 'UNAUTHORIZED';
          break;
        case 403:
          errorMessage = '禁止访问';
          errorCode = 'FORBIDDEN';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          errorCode = 'NOT_FOUND';
          break;
        case 422:
          errorMessage = data?.message || '数据验证失败';
          errorCode = 'VALIDATION_ERROR';
          break;
        case 500:
          errorMessage = '服务器内部错误';
          errorCode = 'SERVER_ERROR';
          break;
        case 502:
          errorMessage = '网关错误';
          errorCode = 'BAD_GATEWAY';
          break;
        case 503:
          errorMessage = '服务不可用';
          errorCode = 'SERVICE_UNAVAILABLE';
          break;
        default:
          errorMessage = data?.message || `请求失败 (${status})`;
          errorCode = `HTTP_${status}`;
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '服务器无响应';
      errorCode = 'NO_RESPONSE';
    } else {
      // 请求配置出错
      errorMessage = error.message || '请求配置错误';
      errorCode = 'REQUEST_ERROR';
    }
    
    // 创建标准化的错误对象
    const normalizedError: ApiError = {
      message: errorMessage,
      code: errorCode as ErrorCode,
      originalError: error,
      status: error.response?.status,
      data: error.response?.data
    };
    
    console.error('标准化错误信息:', normalizedError);
    return Promise.reject(normalizedError);
  }
);

// 导出获取服务器基础URL的工具函数
export const getServerBaseURL = (): string => {
  const port = getBackendPort();
  
  // 优先使用环境变量中的服务器地址
  if (import.meta.env.VITE_SERVER_URL) {
    // 如果URL已经包含端口号，直接使用；否则添加端口号
    const baseUrl = import.meta.env.VITE_SERVER_URL;
    return baseUrl.includes(':') ? baseUrl : `${baseUrl}:${port}`;
  }
  
  // 使用注入的全局变量
  if (typeof __SERVER_URL__ !== 'undefined') {
    // 如果URL已经包含端口号，直接使用；否则添加端口号
    const baseUrl = __SERVER_URL__;
    return baseUrl.includes(':') ? baseUrl : `${baseUrl}:${port}`;
  }
  
  // 默认使用localhost
  return `http://localhost:${port}`;
};

export default api;
