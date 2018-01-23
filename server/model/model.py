import argparse
import pandas as pd
import tensorflow as tf
from sklearn import datasets, metrics


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=1000, type=int,
                    help='number of training steps')

def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the read end of the pipeline.
    return dataset.make_one_shot_iterator().get_next()


def eval_input_fn(features, labels, batch_size):
    """An input function for evaluation or prediction"""
    features=dict(features)
    if labels is None:
        # No labels, use only features.
        inputs = features
    else:
        inputs = (features, labels)

    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices(inputs)

    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)

    # Return the read end of the pipeline.
    return dataset.make_one_shot_iterator().get_next()

def main(argv):
    CSV_COLUMN_NAMES = ['label', 'trip_start','x', 'y']
    DRIVER = ['Yes', 'No']
    train = pd.read_csv("./data/formatted_data/1/train/1.csv", names=CSV_COLUMN_NAMES, header=0)
    test = pd.read_csv("./data/formatted_data/1/test/13.csv", names=CSV_COLUMN_NAMES, header=0)

    args = parser.parse_args(argv[1:])

    train.pop('trip_start')
    test.pop('trip_start')

    train_x, train_y = train, train.pop('label')
    test_x, test_y = test, test.pop('label')

    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))

    classifier = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        hidden_units=[10, 10],
        n_classes=2)

    # Train the Model.
    classifier.train(
        input_fn=lambda:train_input_fn(train_x, train_y, args.batch_size),
        steps=args.train_steps)

    # Evaluate the model.
    eval_result = classifier.evaluate(
        input_fn=lambda:eval_input_fn(test_x, test_y, args.batch_size))

    print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))

    # Generate predictions from the model
    expected = ['Yes', 'No']
    predict_x = {
        'x': [0.0, 5.9],
        'y': [0.0, 3.0],
    }

    predictions = classifier.predict(
        input_fn=lambda:eval_input_fn(predict_x,
                                                labels=None,
                                                batch_size=args.batch_size))

    for pred_dict, expec in zip(predictions, expected):
        template = ('\nPrediction is "{}" ({:.1f}%), expected "{}"')

        class_id = pred_dict['class_ids'][0]
        probability = pred_dict['probabilities'][class_id]

        print(template.format(DRIVER[class_id],
                              100 * probability, expec))

if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)

