import { ref, onUnmounted } from 'vue'
import { getFileList } from '@/service/api.solution'

// 轮询文件解析结果：基于现有 /file/queryFileList 接口
export function useFileParseTask(busiId: string, intervalMs = 2000) {
  const statusCd = ref<'0' | '1' | '2' | 'unknown'>('unknown')
  const fileId = ref<number | null>(null)
  const result = ref<any>(null)
  const error = ref<string | null>(null)
  let timer: any = null

  async function tick() {
    if (!fileId.value) return
    try {
      const res = await getFileList({ busiId, pageNum: 1, pageSize: 10000 })
      const row = (res?.data?.fileList || []).find((x: any) => x.file_id === fileId.value)
      if (!row) return
      statusCd.value = row.status_cd as any
      if (row.status_cd === '1') {
        try {
          const json = JSON.parse(row.title_data)
          result.value = json?.data ? json.data : json
        } catch (e) {
          result.value = null
        }
        stop()
      } else if (row.status_cd === '2') {
        error.value = '解析失败'
        stop()
      }
    } catch (e: any) {
      error.value = e?.message || '查询失败'
    }
  }

  function watch(id: number) {
    stop()
    fileId.value = id
    statusCd.value = '0'
    timer = setInterval(tick, intervalMs)
  }

  function stop() {
    if (timer) { clearInterval(timer); timer = null }
  }

  onUnmounted(stop)

  return { statusCd, fileId, result, error, watch, stop }
}
