"""CORS 快速诊断脚本"""

import subprocess
import sys

import requests


def check_backend_running():
    """检查后端是否运行"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return True, response.status_code
    except Exception as e:
        return False, str(e)


def check_cors_headers(origin):
    """检查CORS响应头"""
    try:
        headers = {"Origin": origin}
        response = requests.options("http://localhost:8000/health", headers=headers, timeout=2)

        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("access-control-allow-origin"),
            "Access-Control-Allow-Methods": response.headers.get("access-control-allow-methods"),
            "Access-Control-Allow-Headers": response.headers.get("access-control-allow-headers"),
            "Access-Control-Allow-Credentials": response.headers.get(
                "access-control-allow-credentials"
            ),
        }

        return cors_headers
    except Exception as e:
        return {"error": str(e)}


def check_multiple_processes():
    """检查是否有多个进程监听8000端口"""
    try:
        result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)

        lines = result.stdout.split("\n")
        port_8000_listeners = []

        for line in lines:
            if ":8000 " in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    port_8000_listeners.append(parts[4])

        if len(port_8000_listeners) > 1:
            return (
                False,
                f"发现 {len(port_8000_listeners)} 个进程监听8000端口: {set(port_8000_listeners)}",
            )
        elif len(port_8000_listeners) == 1:
            return True, f"1个进程监听8000端口 (PID: {port_8000_listeners[0]})"
        else:
            return False, "未发现监听8000端口的进程"
    except Exception as e:
        return None, f"无法检查进程: {e}"


def main():
    print("=" * 70)
    print("CORS 快速诊断")
    print("=" * 70)
    print()

    # 1. 检查后端运行状态
    print("1. 检查后端服务状态...")
    is_running, status = check_backend_running()
    if is_running:
        print(f"   ✅ 后端运行正常 (HTTP {status})")
    else:
        print(f"   ❌ 后端未运行: {status}")
        print()
        print("请先启动后端服务:")
        print("  cd tradebusiness-backend")
        print("  source venv/Scripts/activate")
        print("  python -m uvicorn app.main:app --reload")
        return
    print()

    # 2. 检查进程数量
    print("2. 检查后端进程...")
    process_ok, process_status = check_multiple_processes()
    if process_ok is None:
        print(f"   ⚠️  无法检查进程: {process_status}")
    elif process_ok:
        print(f"   ✅ {process_status}")
    else:
        print(f"   ❌ {process_status}")
        print()
        print("建议停止所有进程后重启:")
        print("  taskkill //F //PID <pid>")
    print()

    # 3. 测试CORS头
    print("3. 测试CORS响应头...")
    test_origins = [
        "http://localhost:3000",  # Admin Frontend
        "http://localhost:3001",  # Client Frontend
        "http://localhost:5173",  # Vite dev server
    ]

    all_ok = True
    for origin in test_origins:
        headers = check_cors_headers(origin)
        if "error" in headers:
            print(f"   ❌ {origin}: {headers['error']}")
            all_ok = False
        else:
            allow_origin = headers.get("Access-Control-Allow-Origin")
            if allow_origin == origin:
                print(f"   ✅ {origin}")
                print(f"      Access-Control-Allow-Origin: {allow_origin}")
                if headers.get("Access-Control-Allow-Credentials"):
                    print(
                        f"      Access-Control-Allow-Credentials: {headers['Access-Control-Allow-Credentials']}"
                    )
            else:
                print(f"   ❌ {origin}")
                print(f"      预期: {origin}")
                print(f"      实际: {allow_origin}")
                all_ok = False
    print()

    # 4. 最终结论
    print("=" * 70)
    if all_ok:
        print("✅ CORS配置正常！前端应该可以正常访问后端API")
    else:
        print("❌ CORS配置有问题，请检查:")
        print("   1. .env 文件中的 CORS_ORIGINS 配置")
        print("   2. 确保后端已重启并使用最新配置")
        print("   3. 检查是否有多个后端进程")
    print("=" * 70)


if __name__ == "__main__":
    main()
