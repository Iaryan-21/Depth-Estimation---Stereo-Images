import numpy as np
import cv2
import glob
from DisparityMap import *
from PoseEstimation import *
from Rectification import *
from EstimateFEmatrix import *
import argparse

def feature_pairs(matches, kp1, kp2):
    pt_img1 = np.array([kp1[match.queryIdx].pt for match in matches]).reshape(-1,2)
    pt_img2 = np.array([kp2[match.trainIdx].pt for match in matches]).reshape(-1,2)

    return pt_img1, pt_img2

def feature_match(image1, image2):
    img1 = image1.copy
    img2 = image2.copy

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    print("Detecting Features")
    sift = cv2.SIFT_create()
    kp1,des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    img_1 = cv2.drawKeypoints(gray1, kp1, img1)
    img_2 = cv2.drawKeypoints(gray2. kp2, img2)
    print("Feature Matching")
    bf = cv2.BFMatcher()
    matches = bf.match(des1, des2)

    matches = sorted(matches, key = lambda x:x.distance)
    matches = matches[:150]

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches, None, flags =2)
    cv2.imwrite('feature_match.png', img3)

    return matches, kp1, kp2

def main():
    parser = argparse.ArgumentParser(description="Depth Estimation from Stereo Image Pairs")
    parser.add_argument('--dataset', required = False, help = 'Dataset name')
    args = parser.parse_args()
    dataset = args.dataset
    

    if dataset =="curule":
        k1 = np.array([[1758.23,0, 977.42], [ 0, 1758.23, 552.15], [0 ,0, 1]])
        k2 = np.array([[1758.23,0 ,977.42], [0,1758.23 ,552.15], [0, 0, 1]])
        baseline=88.39
        f = k1[0,0]

    if dataset=="octagon":
        k1 = np.array([[1742.11, 0 ,804.90], [0 ,1742.11 ,541.22], [0 ,0, 1]])
        k2 = np.array([[1742.11, 0 ,804.90], [0 ,1742.11, 541.22], [0, 0, 1]])
        baseline=221.76
        f = k1[0,0]

    if dataset == "pendulum":
        k1 = np.array([[1729.05, 0 ,-364.24], [0 ,1729.05 ,552.22], [0 ,0, 1]])
        k2 = np.array([[1729.05, 0, -364.2], [0,1729.05, 552.22], [0, 0, 1]])
        baseline=537.75
        f = k1[0,0]
    # path = "Depth_Estimation_Stereo_Images/Data" + str(dataset)
    # images = [cv2.imread(file) for file in sorted(glob.glob(str(path)+'/*.png'))]
    # print("Total Number of images are:", len(images))
    # image1 = images[0]
    # image2 = images[2]
    path = "C:\\Users\\aryan\\OneDrive\\Desktop\\Depth_Estimation_Stereo_Images\\Data\\" + str(dataset)
    file_list = sorted(glob.glob(str(path)+'/*.png'))
    print("Files found:", file_list)
    images = [cv2.imread(file) for file in file_list]
    print("Total Number of images are:", len(images))

    if len(images) > 0:
        image1 = images[0]
        image2 = images[1]
    # rest of your code
    
    
        matches,key_features1,key_features2 = feature_match(image1,image2)
        pt1,pt2  = feature_pairs(matches,key_features1,key_features2) 

        pts1_,pts2_, F = ransac(pt1,pt2)
        print("Estimated F:\n",F)
  
        E = estimate_E(k1,k1,F)
        print("Estimated E:\n",E)


        R,T = extract_pose(E,pts1_,pts2_,k1,k2)
        print("Rotation matrix:\n", R)
        print("Translation:\n",T)


        img1_rectified,img2_rectified,F_rectified = rectify(image1,image2,F,pts1_,pts2_)

        lines1,lines2 = epipolar_lines(pts1_,pts2_,F,img1_rectified,img2_rectified)



        gray1 = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    

        disparity_map =  get_disparity(gray1,gray2,50,2)
        plt.imshow(disparity_map, cmap="gray")
        plt.savefig("disparity.png")

        depth_map = get_depth(disparity_map,baseline,f)
        plt.imshow(depth_map, cmap='hot', interpolation='nearest')
        plt.savefig("depth_map.png")
        plt.imshow(depth_map, cmap='gray', interpolation='nearest')
        plt.savefig("depth_gray.png")
    else:
        print("No images found. Check the file path and file extension.")



if __name__ == '__main__':
    main()
