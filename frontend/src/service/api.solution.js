import { http } from './request';
import axios from 'axios';
// 优先使用环境变量中的后端主机地址，默认回落到本地开发端口
const VITE_SOLUTION_API_BASE_PREFIX = import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847';
const VITE_SOLUTION_API_PROXY_PREFIX = '/api';

/**
 * @description: 登录验证
 * @param {object} data 用户信息
 * @return {promise}
 */
export const solutionLogin = (data) => {
    return http({
        method: 'POST',
        // 后端 auth 路由无前缀，挂在 /api 下
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/login`,
        data,
    });
};

/**
 * @description: 验证token是否过期
 * @param {string} token
 * @return {promise}
 */
export const verifyTokenExpired = (token) => {
    return http({
        method: 'POST',
        // 后端 auth 路由无前缀，挂在 /api 下
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/checkToken`,
        data: { key: token },
    });
};

/**
 * @description: 扩写、润色、续写、改写接口
 * @return {promise}
 */
export const getKnowToWriteUrl = VITE_SOLUTION_API_BASE_PREFIX + VITE_SOLUTION_API_PROXY_PREFIX + "/solution/optimize-content"
/**
 * @description: 生成文章接口
 * @return {promise}
 */
export const createArticleUrl = VITE_SOLUTION_API_BASE_PREFIX + VITE_SOLUTION_API_PROXY_PREFIX + "/solution/generate-article"
export const createChapterUrl = VITE_SOLUTION_API_BASE_PREFIX + VITE_SOLUTION_API_PROXY_PREFIX + "/solution/generate-chapter"
/**
 * @description: 查询写作模板列表
 * @return {promise}
 */
export const selectWritingTemplateList = (data) => {
    return http({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/templateQuery`,
        data
    });
};

/**
 * @description: 查询文件列表
 * @return {promise}
 */
export const getFileList = (data) => {
    return http({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/file/queryFileList`,
        data
    });
};

/**
 * @description: 删除文件
 * @return {promise}
 */
export const deleteFileInfo = (data) => {
    return http({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/file/fileDelete`,
        data
    });
};

/**
 * @description: 文件重命名
 * @return {promise}
 */
export const updateFileName = (data) => {
    return http({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/file/reFilename`,
        data
    });
};
/**
 * @description: 查询标题
 * @return {promise}
 */
export const queryTemplateTitle = (data) => {
    return http({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/titleDataQuery`,
        data
    });
};
/**
 * @description: 文件上传
 * @return {promise}
 */
export const uploadBusiFile = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/file/upload`,
        data: params,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
};
/**
 * @description: 选定查询标题模板
 * @return {promise}
 */
export const selectTemplateTitle = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/file/selectTemplateTitle`,
        data: params
    });
};
/**
 * @description: 标题模板生成
 * @return {promise}
 */
export const createTemplate = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/create`,
        data: params
    });
};
/**
 * @description: 标题模板刷新
 * @return {promise}
 */
export const templateRefresh12 = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/refresh`,
        data: params
    });
};
/**
 * @description: 标题模板保存
 * @return {promise}
 */
export const templateSave = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/templateSave`,
        data: params
    });
};
/**
 * @description: 标题模板删除
 * @return {promise}
 */
export const templateDelete = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/templateDelete`,
        data: params
    });
};
/**
 * @description: 标题模板修改
 * @return {promise}
 */
export const templateUpdate = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/templateUpdate`,
        data: params
    });
};
/**
 * @description: 生成模板接口（入表）
 * @return {promise}
 */
export const templateCreate = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/createTemplateEntryTable`,
        data: params
    });
};
/**
 * @description: 生成模板查询接口
 * @return {promise}
 */
export const createTemplateSelect = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/queryCreateTemplateList`,
        data: params
    });
};
/**
 * @description: 生成模板重命名模板名称
 * @return {promise}
 */
export const createTemplateReName = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/reCreateTemplateName`,
        data: params
    });
};
/**
 * @description: 删除所生成生成模板
 * @return {promise}
 */
export const deleteCreateTemplate = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/deleteCreateTemplate`,
        data: params
    });
};
/**
 * @description: 用户常用模板查询
 * @return {promise}
 */
export const usuallyTemplateQuery = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/queryUsuallyTemplate`,
        data: params
    });
};
/**
 * @description: 全部模板查询
 * @return {promise}
 */
export const allTemplateQuery = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/queryTemplateList`,
        data: params
    });
};
/**
 * @description: 自定义模板重命名模板名称
 * @return {promise}
 */
export const templateReName = (params) => {
    return axios({
        method: 'POST',
        url: `${VITE_SOLUTION_API_BASE_PREFIX}${VITE_SOLUTION_API_PROXY_PREFIX}/templates/reTemplateName`,
        data: params
    });
};
