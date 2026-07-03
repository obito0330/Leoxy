import cv2
import numpy as np

# 读取图像
image = cv2.imread(" ")
# 检查图像是否正确读取
if image is None:
    print("Error: Image not found.")
    exit()

m = image.shape[0]
n = image.shape[1]

cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Original Image',(1536,1024))

# 转换为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)


# 自适应阈值二值化
binary_adaptive = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 3)

# Canny边缘检测
edges = cv2.Canny(blurred, 55, 140)

# 霍夫圆环变换
circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1.2, 115, param1=50, param2=30, minRadius=57, maxRadius=63)

# 确保至少检测到一个圆
if circles is not None:
    # 将circles数组转换为整数，并迭代每个检测到的圆
    circles = np.round(circles).astype("int")
    positive_circles = []  # 用于存储正面圆的圆心坐标
    for (x, y, r) in circles[0, :, :]:
        # 绘制圆心
        cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
        # # 绘制圆轮廓
        # cv2.circle(image, (x, y), r, (0, 255, 0), 2)

# 创建一个与原图大小相同的黑色掩码
mask = np.zeros_like(gray)
for (x,y,r) in circles[0, :, :]:
    # 在掩码上绘制白色圆，确保圆的半径和圆心位置正确
    cv2.circle(mask, (x, y), 15, (255, 255, 255), -1)  # 使用-1填充整个圆形
    # 将掩码应用到边缘检测图像上
    circle_edges = cv2.bitwise_and(edges, mask)

    # 统计边缘数量
    edge_count = np.count_nonzero(circle_edges)

    # 检查边缘数量是否低于5
    if edge_count < 3:
        # 如果是，用红色圆圈标出这个圆,标出的圆环即为正面
        cv2.circle(image, (x, y), r, (0, 0, 255), 3)
        # 将圆心坐标添加到列表中
        positive_circles.append((x, y, r))

    # 重置掩码为黑色，以便下一个圆的计算
    mask.fill(0)

#  # 打印所有正面圆的圆心坐标
# for (x, y, r) in positive_circles:
#      print(f"正面圆的圆心坐标: ({x}, {y})")

# # cv2.namedWindow('blurred', cv2.WINDOW_NORMAL)
# # cv2.namedWindow('edges', cv2.WINDOW_NORMAL)
# # cv2.namedWindow('gray', cv2.WINDOW_NORMAL)
# # cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
# cv2.namedWindow('binary_adaptive', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)

# cv2.resizeWindow('Original Image',int(n/3),int(m/3))
# cv2.resizeWindow('Original Image',3072,2048)
# cv2.resizeWindow('edges',int(n/5),int(m/5))

# cv2.imshow('Original Image', image)
# # cv2.imshow('blurred',blurred)
# # cv2.imshow('edges',edges)
# # cv2.imshow('mask',mask)
# cv2.imshow('binary_adaptive',binary_adaptive)
# # cv2.imshow('circle_binary',circle_binary)
# # cv2.imshow('gray',gray)
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# 孔洞填充
def fill_Image(binary_image):
    # 获取输入图像的高度 h 和宽度 w。binary_image.shape 返回一个包含图像维度的元组，[:2] 取前两个维度（高度和宽度）。
    h, w = binary_image.shape[:2]
    # 创建一个大小为 (h+2, w+2) 的全零掩码图像 mask，数据类型为 uint8。这个掩码用于 floodFill 函数，大小增加2是为了处理边界。
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # floodFill函数中的seedPoint对应像素必须是背景
    # 初始化一个布尔变量 isbreak，用于标记是否找到孔洞的种子点。
    isbreak = False
    # 开始一个循环，遍历图像的每一行（i 表示行索引）
    for i in range(binary_image.shape[0]):
        # 在每一行中，开始另一个循环，遍历每一列（j 表示列索引）。
        for j in range(binary_image.shape[1]):
            # 检查当前像素是否为黑色（值为0），即是否为孔洞的一部分。
            if (binary_image[i][j] == 0):
                # 如果找到一个黑色像素，则将其坐标 (i, j) 赋值给 seedPoint，作为填充的起始点。
                seedPoint = (i, j)
                # 将 isbreak 设置为 True，表示已经找到种子点
                isbreak = True
                break
        if (isbreak):
            break

    # 创建 binary_image 的副本 bw_fill，用于后续的填充操作。
    bw_fill = binary_image.copy()
    # 使用 cv2.floodFill 函数从 seedPoint 开始填充 bw_fill 图像。填充的颜色为白色（值为255），并使用之前创建的 mask 作为掩码。
    cv2.floodFill(bw_fill, np.uint8(mask), seedPoint, 255)
    # 对填充后的图像 bw_fill 进行按位取反（黑变白，白变黑），然后与原始的 binary_image 进行按位或运算。这一步的目的是将填充后的孔洞与原始图像结合，得到最终的结果。
    bw_fill = cv2.bitwise_not(bw_fill) | binary_image
    return bw_fill

# 创建一个与原图大小相同的黑色掩码
mask = np.zeros_like(binary_adaptive)
for (x,y,r) in positive_circles:
    # 在掩码上绘制白色圆，确保圆的半径和圆心位置正确
    cv2.circle(mask, (x, y), r+5, (255, 255, 255), -1)  # 使用-1填充整个圆形
    # 将掩码应用到二值化图像上
    circle_binary = cv2.bitwise_and(binary_adaptive, mask)

    # 调用填充函数
    filled_img = fill_Image(circle_binary)

    # 高斯模糊预处理
    blurred = cv2.GaussianBlur(filled_img, (3, 3), 0)

    # 将与运算后的图像膨胀
    kernel = np.ones((6, 6), np.uint8)
    dilation = cv2.dilate(blurred, kernel)

    # # 高斯模糊预处理
    # blur = cv2.GaussianBlur(dilation, (5, 5), 0)

    # 初始化一个布尔变量gap_found，用于标记是否在圆周上找到了缺口
    gap_found = False
    # 初始化一个列表来存储缺口的坐标和角度
    gaps = []

    # 遍历圆周上的所有点
    for theta in np.linspace(0, 2 * np.pi, 720):
        offset_x = int(r * np.cos(theta))
        offset_y = int(r * np.sin(theta))
        point_x = x + offset_x
        point_y = y + offset_y
        # 确保点在图像范围内
        if 0 <= point_y < image.shape[0] and 0 <= point_x < image.shape[1]:
            # 检查该点是否是缺口
            if dilation[point_y, point_x] == 0:
                gap_found = True
                gap_angle = np.arctan2(offset_y, offset_x)
                gaps.append(((point_x, point_y), gap_angle))
                # 在图像上标记缺口
                cv2.circle(image, (point_x, point_y), 4, (255, 0, 0), -1)

    # 检查是否找到缺口
    if gaps:
        print("Found gaps at coordinates:")
        for gap in gaps:
            print(f"Gap at ({gap[0][0]}, {gap[0][1]}) with angle {np.degrees(gap[1]):.2f} degrees")
    else:
        print("No gaps found.")

    if not gap_found:
        # 如果没有找到缺口，绘制完整的圆环
        cv2.circle(image, (x, y), r, (0, 255, 0), 2)


cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)
# cv2.namedWindow('circle_binary', cv2.WINDOW_NORMAL)
# cv2.namedWindow('binary_adaptive', cv2.WINDOW_NORMAL)
# cv2.namedWindow('clean', cv2.WINDOW_NORMAL)
# cv2.namedWindow('filled_img', cv2.WINDOW_NORMAL)
#
# cv2.resizeWindow('Original Image',int(n/2),int(m/2))
# cv2.resizeWindow('circle_binary',int(n/3),int(m/3))
# cv2.resizeWindow('binary_adaptive',int(n/5),int(m/5))
# cv2.resizeWindow('clean',int(n/5),int(m/5))
# cv2.resizeWindow('filled_img',int(n/3),int(m/3))
#
cv2.imshow('Original Image', image)
# cv2.imshow('circle_binary', circle_binary)
# cv2.imshow('binary_adaptive',binary_adaptive)
# cv2.imshow('clean',clean)
# cv2.imshow('filled_img',filled_img)

cv2.waitKey(0)
cv2.destroyAllWindows()
