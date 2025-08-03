# import os
#
# import cv2
# import numpy as np
#
#
# def extract_by_rgb_ranges(img_bgr, target_rgb=(16, 208, 129), r_tol=15, g_tol=15, b_tol=15):
#     """
#     提取特定颜色的数字区域
#     :param img_bgr: 输入图像(BGR格式)
#     :param target_rgb: 目标颜色(R,G,B)
#     :param r_tol: 红色通道阈值
#     :param g_tol: 绿色通道阈值
#     :param b_tol: 蓝色通道阈值
#     :return: 二值化掩膜
#     """
#
#     target_r = target_rgb[0]
#     target_g = target_rgb[1]
#     target_b = target_rgb[2]
#
#     # 计算各通道范围 (注意OpenCV是BGR顺序！)
#     lower = np.array([
#         max(0, target_b - b_tol),  # B下限
#         max(0, target_g - g_tol),  # G下限
#         max(0, target_r - r_tol)  # R下限
#     ], dtype=np.uint8)
#
#     upper = np.array([
#         min(255, target_b + b_tol),  # B上限
#         min(255, target_g + g_tol),  # G上限
#         min(255, target_r + r_tol)  # R上限
#     ], dtype=np.uint8)
#
#     # 生成掩膜
#     mask = cv2.inRange(img_bgr, lower, upper)
#     return mask
#
#
# def show_scaled(name, img, scale=3.0, wait=True):
#     """辅助函数：缩放显示图像"""
#     h, w = img.shape[:2]
#     resized = cv2.resize(img, (int(w*scale), int(h*scale)),
#                          interpolation=cv2.INTER_NEAREST)
#     cv2.imshow(name, resized)
#     if wait:
#         key = cv2.waitKey(0)
#         if key == ord('q'):  # 按q键提前退出调试
#             return False
#     return True
#
#
# def split_and_recognize(img_bgr, templates, debug=False, debug_scale=3.0):
#     """完整数字识别流程（带放大调试功能）"""
#
#
#     # 1. 颜色过滤
#     binary_mask = extract_by_rgb_ranges(img_bgr)
#     if debug:
#         print("\n=== 调试模式 ===")
#         print(f"原始图像尺寸: {img_bgr.shape} | 二值图尺寸: {binary_mask.shape}")
#         if not show_scaled("1. 颜色过滤结果", binary_mask):
#             return ""
#         show_scaled("template", templates[3])
#
#     # 2. 查找轮廓
#     contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if debug:
#         contour_img = img_bgr.copy()
#         cv2.drawContours(contour_img, contours, -1, (0,255,0), 2)
#         print(f"\n找到 {len(contours)} 个轮廓")
#         if not show_scaled("2. 轮廓检测", contour_img):
#             return ""
#
#     # 3. 提取候选区域
#     digit_rois = []
#     for i, cnt in enumerate(contours):
#         x, y, w, h = cv2.boundingRect(cnt)
#         if w < 5 or h < 10:  # 过滤过小区域
#             if debug:
#                 print(f"  轮廓{i} 被过滤 (x={x}, y={y}, w={w}, h={h})")
#             continue
#
#         roi = binary_mask[y:y+h, x:x+w]
#         digit_rois.append((x, roi))
#
#         if debug:
#             print(f"  轮廓{i}: x={x}, y={y}, w={w}, h={h}, 面积={w*h}")
#             marked_roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
#             if not show_scaled(f"3. ROI {i}", marked_roi,  debug_scale*2):  # 特别放大ROI
#                 return ""
#
#     if not digit_rois:
#         if debug:
#             print("!!! 未找到有效数字区域 !!!")
#         return ""
#
#     # 4. 模板匹配
#     results = []
#     for x, roi in sorted(digit_rois, key=lambda x: x[0]):
#         if debug:
#             print(f"\n正在匹配 ROI (x={x}, 尺寸={roi.shape}):")
#
#         best_digit = None
#         max_score = -1
#
#         for digit, template in templates.items():
#             # 计算缩放比例（保持宽高比）
#             scale_h = roi.shape[0] / template.shape[0]
#             scale_w = roi.shape[1] / template.shape[1]
#             scale = min(scale_h, scale_w)
#
#             # 数字1允许更大缩放范围
#             if digit == 1:
#                 if scale < 0.3 or scale > 3.0:
#                     if debug:
#                         print(f"  跳过 {digit}: 缩放比例 {scale:.2f} 超出1的范围")
#                     continue
#             else:
#                 if scale < 0.7 or scale > 1.3:
#                     if debug:
#                         print(f"  跳过 {digit}: 缩放比例 {scale:.2f} 超出常规范围")
#                     continue
#
#             # 调整模板大小
#             resized = cv2.resize(template, (roi.shape[1], roi.shape[0]))
#             score = cv2.matchTemplate(roi, resized, cv2.TM_CCOEFF_NORMED)[0][0]
#
#             if debug:
#                 print(f"  模板 {digit}: 分数={score:.3f} (缩放={scale:.2f})")
#                 blend = np.hstack([roi, resized])
#                 if not show_scaled(f"  ROI vs 模板{digit}", blend):
#                     return ""
#
#             if score > max_score and score > 0.5:
#                 max_score = score
#                 best_digit = digit
#
#         if best_digit is not None:
#             if debug:
#                 print(f"  => 最佳匹配: {best_digit} (分数={max_score:.3f})")
#             results.append((x, str(best_digit)))
#         elif debug:
#             print("  => 无匹配结果")
#
#     # 5. 输出最终结果
#     final_result = ''.join([d for _, d in sorted(results, key=lambda x: x[0])])
#     if debug:
#         print(f"\n最终结果: {final_result}")
#
#     return final_result
#
#
# def adjust_rgb_interactive():
#     img = cv2.imread("templates/3.png")
#     cv2.namedWindow("RGB Adjust")
#
#     # 创建滑动条
#     cv2.createTrackbar("R tol", "RGB Adjust", 5, 50, lambda x: None)
#     cv2.createTrackbar("G tol", "RGB Adjust", 15, 50, lambda x: None)
#     cv2.createTrackbar("B tol", "RGB Adjust", 10, 50, lambda x: None)
#
#     while True:
#         r_tol = cv2.getTrackbarPos("R tol", "RGB Adjust")
#         g_tol = cv2.getTrackbarPos("G tol", "RGB Adjust")
#         b_tol = cv2.getTrackbarPos("B tol", "RGB Adjust")
#
#         mask = extract_by_rgb_ranges(
#             img,
#             target_rgb=(16, 203, 126),
#             r_tol=r_tol,
#             g_tol=g_tol,
#             b_tol=b_tol
#         )
#
#         cv2.imshow("Preview", mask)
#         if cv2.waitKey(1) == 27:
#             break
#
# def debug_templates(templates, save_path=None):
#     """
#     显示/保存所有预处理后的模板图像
#     :param templates: 模板字典 {数字: 模板图像}
#     :param save_path: 如需保存路径，例如 "./template_debug/"
#     """
#     # 创建画布（每行显示5个模板）
#     rows = 2 if len(templates) > 5 else 1
#     cols = min(5, len(templates))
#     canvas = np.zeros((rows*100, cols*100), dtype=np.uint8)
#
#     for i, (digit, template) in enumerate(templates.items()):
#         # 调整模板大小以适应画布
#         resized = cv2.resize(template, (80, 80))
#         row = i // cols
#         col = i % cols
#         canvas[row*100:row*100+80, col*100:col*100+80] = resized
#
#         # 添加数字标签
#         cv2.putText(canvas, str(digit), (col*100 + 30, row*100 + 90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
#
#     # 显示或保存
#     if save_path:
#         os.makedirs(save_path, exist_ok=True)
#         cv2.imwrite(os.path.join(save_path, "all_templates.png"), canvas)
#     show_scaled("Processed Templates", canvas)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#
# if __name__ == "__main__":
#     img = cv2.imread("../image/bad_case.png")
#     # templates = {i: cv2.imread(f"../image/{i}.png", 0) for i in range(10)}
#
#     templates = {}
#
#     for i in range(10):
#         # 先以彩色模式读取模板
#         template_bgr = cv2.imread(f'../image/{i}.png')
#         assert template_bgr is not None, f"模板{i}.png加载失败"
#
#         # 对模板应用相同的RGB过滤
#         template_mask = extract_by_rgb_ranges(template_bgr)
#
#         # 将过滤后的二值图作为模板
#         templates[i] = template_mask
#
#     debug_templates(templates)
#
#     # 识别数字
#     result = split_and_recognize(img, templates, debug=True)
#     print("识别结果:", result)

print(8 / 2 * (2+2))