import os.path

import cv2
import numpy as np
from pathlib import Path

templates = {}
for i in range(10):  # 注意是0-9，共10个数字
    template = cv2.imread(os.path.join(Path(__file__).parent, f'templates/{i}.png'), cv2.IMREAD_GRAYSCALE)
    if template is not None:
        templates[i] = template
    else:
        print(f"警告：模板 {i}.png 未找到！")

def recognize_digits(img, match_threshold=0.8, overlap_threshold=0.7):
    """识别图像中的所有数字，返回数字字符串"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    digits_info = []  # 存储数字及其位置

    # 对每个数字模板进行匹配
    for digit, template in templates.items():
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= match_threshold)  # 获取所有匹配位置

        # 记录匹配结果（数字、x坐标、匹配值）
        for pt in zip(*loc[::-1]):
            digits_info.append({
                "digit": digit,
                "x": pt[0],
                "score": res[pt[1], pt[0]]  # 匹配分数
            })

    # 非极大值抑制（NMS）去除重叠框
    digits_info = sorted(digits_info, key=lambda x: -x["score"])  # 按分数降序
    filtered_digits = []
    for info in digits_info:
        x, digit = info["x"], info["digit"]
        overlap = False
        # 检查是否与已选区域重叠
        for selected in filtered_digits:
            if abs(x - selected["x"]) < template.shape[1] * overlap_threshold:  # 重叠阈值
                overlap = True
                break
        if not overlap:
            filtered_digits.append(info)

    # 按x坐标排序，拼接成字符串
    filtered_digits.sort(key=lambda x: x["x"])
    return ''.join(str(d["digit"]) for d in filtered_digits)


class Reader(object):
    def __init__(self):
        self.template_groups = {}
        self.option_failed_template = None
        self.load_templates()

    def load_templates(self):
        """加载所有模板（兼容无前缀和多前缀）"""
        template_dir = Path(__file__).parent / "templates"

        # 先加载默认模板（0.png~9.png）
        default_group = {}
        for i in range(10):
            path = template_dir / f"{i}.png"
            if path.exists():
                template = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    _, binary = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                    default_group[i] = binary

        if default_group:
            self.template_groups["default"] = default_group

        # 再加载带前缀的模板（prefix_0.png~prefix_9.png）
        font_prefixes = set()
        for f in template_dir.glob("*_*.png"):
            parts = f.stem.split('_')
            if len(parts) == 2 and parts[1].isdigit():
                font_prefixes.add(parts[0])

        for prefix in sorted(font_prefixes):
            group = {}
            for i in range(10):
                path = template_dir / f"{prefix}_{i}.png"
                if path.exists():
                    template = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        _, binary = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                        group[i] = binary

            if len(group) == 10:
                self.template_groups[prefix] = group

        template = cv2.imread(str(f"{template_dir}/option_failed.png"), cv2.IMREAD_GRAYSCALE)
        _, binary = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
        self.option_failed_template = binary

        if not self.template_groups:
            raise FileNotFoundError("未找到有效的模板文件！")

    def detect_template(self, img, match_threshold=0.7):
        """检测option_failed_template是否存在于图像中

        Args:
            img: 输入图像 (可以是PIL Image或OpenCV格式)
            match_threshold: 匹配阈值，默认0.7

        Returns:
            bool: 如果模板存在返回True，否则返回False
        """
        if self.option_failed_template is None:
            return False
        img = np.array(img)
        # 转换图像格式
        if len(img.shape) == 3:  # 如果是彩色图像
            if img.shape[2] == 3:  # RGB
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
            elif img.shape[2] == 4:  # RGBA
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
        else:
            img_cv = img  # 已经是灰度图

        # 执行模板匹配
        res = cv2.matchTemplate(img_cv, self.option_failed_template, cv2.TM_CCOEFF_NORMED)
        max_val = cv2.minMaxLoc(res)[1]  # 获取最大匹配值

        return max_val >= match_threshold

    def recognize_digits(self, img, match_threshold=0.7, overlap_threshold=0.7):
        """识别数字（兼容多字体）"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        digits_info = []

        # 对每个字体组进行匹配
        for font_name, templates in self.template_groups.items():
            for digit, template in templates.items():
                res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= match_threshold)

                for pt in zip(*loc[::-1]):
                    digits_info.append({
                        'digit': digit,
                        'x': pt[0],
                        'score': res[pt[1], pt[0]],
                        'font': font_name
                    })

        # 非极大值抑制
        digits_info.sort(key=lambda x: -x['score'])
        filtered = []
        for info in digits_info:
            x = info['x']
            overlap = any(
                abs(x - sel['x']) < max(
                    self.template_groups[info['font']][info['digit']].shape[1],
                    self.template_groups[sel['font']][sel['digit']].shape[1]
                ) * overlap_threshold
                for sel in filtered
            )
            if not overlap:
                filtered.append(info)

        filtered.sort(key=lambda x: x['x'])
        return ''.join(str(d['digit']) for d in filtered)

    def image_to_string(self, img):
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return self.recognize_digits(img_cv)




if __name__ == '__main__':
    import time
    from utils import get_windowshot
    img = get_windowshot([2128, 1133, 2413, 1191])  # 假设返回的是PIL Image
    ocr = Reader()
    t = time.time()
    result = ocr.image_to_string(img)
    print("识别结果:", result, "延迟:", time.time() - t)