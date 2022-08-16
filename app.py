import os
import cv2
import time

REAL_FINGERPRINT_DIRECTORY = "SOCOFing/Real"

sift_algo = cv2.SIFT_create()
scanned_fingerprint_filename = "SOCOFing/Custom/110__F_Left_index_finger_-5deg.bmp"


def fetchScannedFinger(filename):
    # Viewing Sample Fingerprint

    scanned_finger = cv2.imread(filename)

    # Using SIFT Algorithm, find key points and descriptors

    key_points_scanned, descriptors_scanned = sift_algo.detectAndCompute(scanned_finger, None)

    # scaled_scanned_finger = cv2.resize(scanned_finger, None, fx=4, fy=4) scanned_kp = cv2.drawKeypoints(
    # scaled_scanned_finger, key_points_scanned, 0, (0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
    # cv2.imshow("Scanned Images KPs: ", scanned_kp) cv2.waitKey(0) cv2.destroyAllWindows()

    # cv2.imshow("Scanned Fingerprint to be matched with database",scanned_finger)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return key_points_scanned, descriptors_scanned, scanned_finger


def findBestMatch(key_points_scanned, descriptors_scanned, scanned_finger, flann_params, threshold):
    func_start_time = time.time()
    ## Finding Best match with stored fingerprints

    best_score = 0
    best_filename = None
    best_image = None

    kp1 = key_points_scanned
    kp2 = mp = None

    progress_counter = 0

    # ! Tune param: [:x] => first x number of best_images to select
    for file in os.listdir(REAL_FINGERPRINT_DIRECTORY):

        # Small progress counter to terminal
        if progress_counter % 10 == 0:
            print("Matched " + str(progress_counter) + " finger images so far")
            print("Last file compared: " + file)
        progress_counter += 1
        #

        # Read stored fingerprint and create SIFT descriptor
        fingerprint_best_image = cv2.imread(REAL_FINGERPRINT_DIRECTORY + "/" + file)

        key_points_stored, descriptors_stored = sift_algo.detectAndCompute(fingerprint_best_image, None)

        # Using Fastest-Library-for-Approx-Nearest-Neighbours
        matches = cv2.FlannBasedMatcher(flann_params, {}). \
            knnMatch(descriptors_scanned, descriptors_stored, k=2)

        # Finding Close matched key points
        match_points = []

        for p, q in matches:
            # ! param: neighbour distance threshold 0.1
            if p.distance < threshold * q.distance:
                match_points.append(p)

        # picking min number of key points
        number_of_keypoints = min(len(key_points_scanned), len(key_points_stored))

        # Checking if new matched points beats the score for any previous stored fingerprint
        # If the new score has more matched keypoints it is a better match
        new_score = len(match_points) / number_of_keypoints * 100
        # print("N.Score:" + str(new_score))
        if new_score > best_score:
            best_score = new_score
            best_filename = file
            best_image = fingerprint_best_image
            kp2 = key_points_stored
            mp = match_points

        # End Keypoint matcher loop

    print(best_filename)
    print(str(best_score))
    func_end_time = time.time()

    if best_filename is None or best_score == 0:
        print("No Suitable Fingerprint Match was found")

    else:
        result_title = "Best matched file: " + str(best_filename) + " with score: " + str(best_score)

        result = cv2.drawMatches(scanned_finger, kp1, best_image, kp2, mp, None)
        result = cv2.resize(result, None, fx=4, fy=4)
        cv2.imshow(result_title, result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("Total Matching Execution Time: " + str(func_end_time - func_start_time))


if __name__ == "__main__":
    key_points_scanned, descriptors_scanned, scanned_finger = fetchScannedFinger(scanned_fingerprint_filename)

    # Different Nearest Neighbour Matchers
    FLANN_INDEX_KDTREE = 0
    FLANN_INDEX_LSH = 1
    flann_matcher_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=10)
    # flann_matcher_params = dict(algorithm=FLANN_INDEX_LSH,
    #                             table_number=6,
    #                             key_size=12,
    #                             multi_probe_level=1)
    findBestMatch(key_points_scanned, descriptors_scanned, scanned_finger, flann_matcher_params, 0.2)
