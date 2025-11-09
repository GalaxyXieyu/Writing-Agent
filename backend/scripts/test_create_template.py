"""
自测脚本：调用 /api/templates/createTemplateEntryTable

特性：
- 先尝试获取默认模型 /api/model-config/default
- 若无默认模型，则从 /api/model-config/list 取一个可用模型
- 构造示例请求体并发起创建模板请求
- 打印状态码、响应 JSON/文本，便于定位 500 根因

使用：
  python3 backend/scripts/test_create_template.py [--host http://localhost:29847]
"""
from __future__ import annotations
import sys
import json
import time
import urllib.request
import urllib.parse


def http_get(url: str):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.getcode(), body
    except Exception as e:
        return None, f"GET {url} error: {e}"


def http_post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json;charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.getcode(), body
    except Exception as e:
        if hasattr(e, 'read') and callable(e.read):
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            return getattr(e, 'code', None), f"{e}\n{body}"
        return None, f"POST {url} error: {e}"


def pick_model_id(base: str) -> int | None:
    # 1) 尝试默认模型
    code, body = http_get(f"{base}/api/model-config/default")
    if code == 200:
        try:
            data = json.loads(body)
            if data.get("code") == 200 and data.get("data"):
                return data["data"].get("id")
        except Exception:
            pass
    # 2) 列表兜底，取第一个
    code, body = http_get(f"{base}/api/model-config/list?page=1&page_size=1&status_cd=Y")
    if code == 200:
        try:
            data = json.loads(body)
            rows = (data.get("data") or {}).get("list") or []
            if rows:
                return rows[0].get("id")
        except Exception:
            pass
    return None


def main():
    base = "http://localhost:29847"
    if len(sys.argv) >= 3 and sys.argv[1] == "--host":
        base = sys.argv[2]
    print(f"Using host: {base}")

    model_id = pick_model_id(base)
    print(f"Picked model_id: {model_id}")
    if model_id is None:
        print("未找到任何可用模型。请在后端添加模型配置，并设置为默认或使用前端选择模型。")
        sys.exit(2)

    payload = {
        "titleName": "AI 报告生成",
        "writingRequirement": "目标、未来、背景",
        "userId": "13800000000",
        "templateName": f"自测模板-{int(time.time())}",
        "modelId": model_id,
    }
    url = f"{base}/api/templates/createTemplateEntryTable"
    print("POST", url)
    print("Payload:", json.dumps(payload, ensure_ascii=False))
    code, body = http_post_json(url, payload)
    print("Status:", code)
    try:
        parsed = json.loads(body)
        print("Response(JSON):", json.dumps(parsed, ensure_ascii=False, indent=2))
    except Exception:
        print("Response(Text):", body)


if __name__ == "__main__":
    main()
