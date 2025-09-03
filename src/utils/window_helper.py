import win32con
import win32gui


def bring_window_to_front(hwnd):
    """将指定窗口置于前台"""
    try:
        # 如果窗口最小化，先恢复
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 将窗口置于前台
        win32gui.SetForegroundWindow(hwnd)

        # 激活窗口
        win32gui.BringWindowToTop(hwnd)

        return True
    except Exception as e:
        print(f"设置窗口在前失败: {e}")
        return False
