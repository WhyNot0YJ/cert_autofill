import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

export const applicationAPI = {
  // 获取申请书列表
  getApplications(params?: {
    page?: number
    per_page?: number
    status?: string
    search?: string
  }) {
    return axios.get(`${API_BASE_URL}/applications`, { params })
  },

  // 获取申请书详情
  getApplication(applicationId: number) {
    return axios.get(`${API_BASE_URL}/applications/${applicationId}`)
  },

  // 更新申请书
  updateApplication(applicationId: number, data: any) {
    return axios.put(`${API_BASE_URL}/applications/${applicationId}`, data)
  },

  // 删除申请书
  deleteApplication(applicationId: number) {
    return axios.delete(`${API_BASE_URL}/applications/${applicationId}`)
  },

  // 搜索申请书
  searchApplications(params: {
    q?: string
    status?: string
    date_from?: string
    date_to?: string
  }) {
    return axios.get(`${API_BASE_URL}/applications`, { params })
  }
} 