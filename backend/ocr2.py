import cv2
import numpy as np
from pathlib import Path

class DigitReader:
    def __init__(self):
        self.template_groups = {}
        self.load_templates()

    def preprocess_image(self, img):
        """统一预处理流程（必须与识别时的处理一致）"""
        # 转为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

        # 二值化（使用与目标图像相同的阈值方法）
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        # 形态学处理（可选，消除噪点）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        return processed

    def load_templates(self):
        """加载并标准化所有模板"""
        template_dir = Path(__file__).parent / "templates"

        # 加载无前缀模板（0.png~9.png）
        default_group = {}
        for i in range(10):
            path = template_dir / f"{i}.png"
            if path.exists():
                img = cv2.imread(str(path))
                if img is not None:
                    default_group[i] = self.preprocess_image(img)

        if len(default_group) == 10:
            self.template_groups["default"] = default_group
            print("Loaded default templates (0-9.png)")

        # 加载带前缀模板（prefix_0.png~prefix_9.png）
        font_prefixes = set()
        for f in template_dir.glob("*_*.png"):
            if f.stem.count('_') == 1 and f.stem.split('_')[1].isdigit():
                font_prefixes.add(f.stem.split('_')[0])

        for prefix in font_prefixes:
            group = {}
            for i in range(10):
                path = template_dir / f"{prefix}_{i}.png"
                if path.exists():
                    img = cv2.imread(str(path))
                    if img is not None:
                        group[i] = self.preprocess_image(img)

            if len(group) == 10:
                self.template_groups[prefix] = group
                print(f"Loaded font group: '{prefix}'")

        if not self.template_groups:
            raise FileNotFoundError("No valid templates found!")

    def recognize_digits(self, img, match_threshold=0.7):
        """识别数字"""
        # 对待识别图像做相同预处理
        processed_img = self.preprocess_image(img)

        digits_info = []
        for font_name, templates in self.template_groups.items():
            for digit, template in templates.items():
                res = cv2.matchTemplate(processed_img, template, cv2.TM_CCOEFF_NORMED)
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
                ) * 0.7
                for sel in filtered
            )
            if not overlap:
                filtered.append(info)

        filtered.sort(key=lambda x: x['x'])
        return ''.join(str(d['digit']) for d in filtered)

# 使用示例
if __name__ == '__main__':
    # 初始化阅读器（会自动预处理模板）
    reader = DigitReader()

    # 测试图像（自动应用相同预处理）
    test_img = cv2.imread("../image/img.png")
    if test_img is not None:
        result = reader.recognize_digits(test_img)
        print("识别结果:", result)