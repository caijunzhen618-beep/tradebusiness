import request from './request'

export interface UploadedFile {
  filename: string
  unique_filename: string
  path: string
  url: string
  size: number
  content_type: string
  uploaded_at: string
}

export function uploadAttachment(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request<UploadedFile>({
    url: '/api/v1/files/upload/attachment',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export function uploadLogo(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request<UploadedFile>({
    url: '/api/v1/files/upload/logo',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
