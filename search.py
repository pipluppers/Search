import pandas as pd
import random
import numpy as np
import math

def main():
    print('Welcome to Alex Nguyen\'s Feature Selection Algorithm.')
    fileName = input('Type in the name of the file to test: ')
    if fileName[6:9] == 'BIG':
        df = pd.read_csv(fileName, sep='\s+', names=['Class Label', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
            '29','30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40','41', '42', '43', '44', '45', '46',
            '47', '48','49', '50'])
    else:
        # \s is space. \s+ is at least one space. Small dataset has 10 features
        df = pd.read_csv(fileName, sep='\s+', names=['Class Label', '1', '2', '3', '4','5', '6', '7', '8', '9', '10'])
    print('\nType in the name of the algorithm you want to run.\n')
    print('\t1) Forward Selection\n\t2) Backwards Elimination\n\t3) Alex\'s Special Algorithm\n')
    algo_choice = input('\t\t\t')
    print('\nThis dataset has %d features (not including the class attribute), with %d instances' % (df.shape[1]-1, df.shape[0]))
    print('\nPlease wait while I normalize the data...', end='')
    #   Min-Max Normalization
    new_df = (df - df.min()) / (df.max() - df.min())
    new_df['Class Label'] = df['Class Label']   # Don't change the class labels
    print('\tDone!')
    if algo_choice == '1':
        feature_search(new_df,1)
    elif algo_choice == '2':
        backwards_elimination(new_df)
    elif algo_choice == '3':
        feature_search(new_df,3)

'''
    Nearest Neighbor Algorithm
        Inputs:     - One row for the test set, many rows of training set, list of column names, row of the test data
        Process:    - Do Euclidean Distance between all data points. Use a loop to find the smallest distance. 
        Output:     - Class Label
'''
def nearest_neighbor(test, train, feature, bitmap, test_row):
    bsf_dist = np.inf       #   Best-so-far Distance
    classs = 0              #   The label's class
    for i in range (0, train.shape[0]+1):
        dist = 0
        if i != test_row:
            for j in range(0, train.shape[1]-1):
                dist = dist + bitmap[0][j] * ((float(test[feature[j+1]]) -
                    float(train.loc[i:i][feature[j+1]]))**2)
            dist = np.sqrt(dist)
            if (dist < bsf_dist):
                bsf_dist = dist
                classs = train.loc[i:i][feature[0]]
    return classs.item()

'''
    Leave-One-Out Cross Validation
        Inputs:     - Dataset, current set of features, feature to add, max number of incorrect features, algorithm used
        Process:    - Create a bitmap and update with 1s on the features being considered
                    - Call one of the other cross-validation algorithms which will call Nearest Neighbor
                    - The non-special algorithm just does standard modeling. The special algorithm does pruning
        Outputs:    - Accuracy
'''
def leave_one_out_cross_validation_template(dataset, current_set, feature_to_add, numIncorrect, algo_choice):
    bitmap = np.zeros((1, dataset.shape[1] - 1), dtype=float)
    features = dataset.columns
    for a in range(0, len(current_set)):
        bitmap[0][int(current_set[a]) - 1] = 1  # Make all current features 1's
    bitmap[0][int(feature_to_add) - 1] = 1  # Make the considered feature a 1
    if algo_choice == 1 or 2:
        return leave_one_out_cross_validation(dataset, bitmap, features)
    elif algo_choice == 3:
        return leave_one_out_cross_validation_special(dataset, numIncorrect, bitmap, features)
    else:
        return -1           # This should never be reached

def leave_one_out_cross_validation(dataset, bitmap, features):
    num_correct = 0
    for i in range(0, dataset.shape[0]):  # in range(0, 100)     0->99
        test_set = dataset.loc[i:i]
        df1 = dataset.loc[0:(i - 1)]
        df2 = dataset.loc[i + 1:dataset.shape[0]]  # Should be dataset.loc[i+1, 100]
        training_set = pd.concat([df1, df2])
        if nearest_neighbor(test_set, training_set, features, bitmap, i) \
                == test_set[features[0]].item():
            num_correct += 1
    return (num_correct / dataset.shape[0])

def leave_one_out_cross_validation_special(dataset, numIncorrect, bitmap, features):
    num_correct = 0
    num_wrong = 0
    for i in range(0, dataset.shape[0]):     # in range(0, 100)     0->99
        test_set = dataset.loc[i:i]
        df1 = dataset.loc[0:(i-1)]
        df2 = dataset.loc[i+1:dataset.shape[0]]        # Should be dataset.loc[i+1, 100]
        training_set = pd.concat([df1,df2])
        if nearest_neighbor(test_set, training_set, features, bitmap, i)\
                == test_set[features[0]].item():
            num_correct += 1
        else:
            num_wrong += 1
        if num_wrong > numIncorrect:                #   Pruning step
            return 0
    return (num_correct / dataset.shape[0])

'''
    Feature Search (Forward Selection) and Original Search (Pruning)
        Start with no initial features
        Loop through the levels of the tree (size is number of features)
        Make a bsf accuracy
        Find the accuracy of a feature using the leave-one-out cross validation method. Use algorithm choice to decide which one to call
        It it's better than our bsf, update it and add the best feature to our current set of features
'''
def feature_search(data, algo_choice):
    current_features = {}   #   Dictionaries are easier to search for membership
    current_features_list = []
    bsf_set = []
    absolute_bsf = 0        # If something falls below this, stop

    print('\nBeginning Search.')
    #   Iterating through the rows
    for i in range(0, data.shape[1]-1):     # should be 0 to 10
        #print('On level %d of search tree' % (i+1))
        best_so_far_accuracy = 0
        num_Incorrect = data.shape[0]             # On first try, we should not prune
        #   Iterating through the columns
        for j in range(0, data.shape[1] - 1):
            if not (j+1) in current_features:       #   Using the dictionary
                #print('-- Considering adding feature %d\n' % (j+1))
                accuracy = leave_one_out_cross_validation_template(data, current_features_list, j + 1, num_Incorrect, algo_choice)
                print('\tUsing feature(s) {%d' % (j+1), end='')
                for bb in range(0, len(current_features_list)):
                    print(', %d' % current_features_list[bb], end='')
                print('}, accuracy is %f%%' % (accuracy * 100))
                if accuracy > best_so_far_accuracy:
                    best_so_far_accuracy = accuracy
                    feature_to_add = j + 1
                    num_Incorrect = data.shape[0] - accuracy*data.shape[0]      #   Added
        current_features[feature_to_add] = ''
        current_features_list.append(feature_to_add)
        print('Added feature %d to the current set' % feature_to_add)
        print('Feature set {', end='')
        for bc in range(0, len(current_features_list)):
            print('%d' % current_features_list[bc], end = '')
            if (bc != len(current_features_list) - 1):
                print(', ', end='')
        print('} was best. Accuracy was %f%%' % (best_so_far_accuracy * 100))
        if i == 0:
            absolute_bsf = best_so_far_accuracy
            bsf_set.append(feature_to_add)
        elif best_so_far_accuracy >= absolute_bsf:
            absolute_bsf = best_so_far_accuracy
            bsf_set.append(feature_to_add)
        else:
            if (best_so_far_accuracy < absolute_bsf):       # Can most likely take this out
                print('(WARNING!) Accuracy has decreased! Continue search in case of local maxima)')
        print('')
    print('Finished Search!! The best feature subset is {', end='')
    for bd in range (0, len(bsf_set)):
        print('%d' % bsf_set[bd], end = '')
        if (bd != len(bsf_set) - 1):
            print(', ', end='')
    print('}, which has an accuracy of %f%%' % absolute_bsf * 100)

def backwards_elimination(data):
    removed_features = {}
    removed_features_list = []
    bsf_set = []
    absolute_bsf_accuracy = 0
    current_features_list = []
    for count in range(0, data.shape[1] - 1):
        current_features_list.append(count + 1)
    #   Don't care about feature to add. Just pick a random one inside the current features so bitmap works nicely
    print('\nBeginning search.')
    default_acc = leave_one_out_cross_validation_template(data, current_features_list,current_features_list[0], 0, 2)
    absolute_bsf_accuracy = default_acc
    for i in range(0, data.shape[1] - 2):       # Ran once above
        best_so_far_acc = 0
        for j in range(0, data.shape[1]-1):
            current_features_list = []
            if not (j+1) in removed_features:
                print('-- Considering removing feature %d' % (j+1))
                for k in range(0, data.shape[1] - 1):
                    if (k+1) not in removed_features and k != j:
                        current_features_list.append(k+1)           # Add everything that is not removed and is not being removed in current list
                accuracy = leave_one_out_cross_validation_template(data, current_features_list, current_features_list[0], 0, 2)      # Find the accuracy of that
                print('\tUsing feature(s) {%d' % current_features_list[0], end='')
                for bb in range(1, len(current_features_list)):
                    print(', %d' % current_features_list[bb], end='')
                print('}, accuracy is %f%%' % (accuracy * 100))
                if accuracy > best_so_far_acc:
                    best_so_far_acc = accuracy
                    feature_to_remove = j + 1
        removed_features_list.append(feature_to_remove)
        removed_features[feature_to_remove] = ''
        print('Removed feature %d and got an accuracy of %f%%' % (feature_to_remove, best_so_far_acc*100))
        if best_so_far_acc >= absolute_bsf_accuracy:
            absolute_bsf_accuracy = best_so_far_acc
            bsf_set = removed_features_list
        else:
            print('(WARNING) Accuracy has decreased! Continuing search in case of local optima')
    print('Finished Search! The best feature subset is {', end='')
    for r in range(0, data.shape[1]-1):
        if not (r + 1) in removed_features:  # Using the dictionary
            print('%d' % r + 1, end = '')
            if r != data.shape[1] - 1:
                print(', ', end = '')
    print('} which has an accuracy of %f%%' % (absolute_bsf_accuracy * 100))

if __name__ == "__main__":
    main()
