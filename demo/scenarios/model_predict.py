import argparse
import logging
import os
import sys
import time
from resource import *
from typing import Optional
import tensorflow as tf
import garden

def setup_log():
    logging.basicConfig(
        filename="./log.txt",
        format="%(asctime)s %(message)s",
        level=logging.DEBUG,
    )


def print_and_log(message: Optional[str]):
    """Print to console, as well as log to file."""
    print(message, flush=True)
    logging.info(message)


def load_log() -> str:
    """Loads the log contents and returns it as a string."""
    with open("log.txt", "r") as f:
        content = f.read()
    return content


def parse_args():
    """Parse any command line args."""

    parser = argparse.ArgumentParser(
        description="Command line arguments for the model performance tester."
    )
    parser.add_argument(
        "--images",
        help="The directory that contains the images to use for testing model performance.",
        required=True,
    )
    # --model file example: model_f3_a.json
    parser.add_argument(
        "--model", help="The json formatted model file.", required=True
    )
    # --weights file example: model_f_a.h5
    parser.add_argument(
        "--weights",
        help="The file that contains the model weights.",
        required=True,
    )
    args = parser.parse_args()
    return args


def run_model(image_folder_path, model_file, weights_file):
    """
    This script gets performance metrics (elapsed time and memory consumption) for running inference on a model.
    It does NOT check accurate predictions - it simply runs the inference on the provided dataset and outputs statics
    on elapsed time and memory consumption.
    """
    setup_log()

    # getrusage returns Kibibytes on linux and bytes on MacOS
    r_mem_units_str = "KiB" if sys.platform.startswith("linux") else "bytes"

    import tensorflow as tf

    print_and_log(f"TensorFlow version: {tf.__version__}")
    from tensorflow.keras.models import model_from_json

    # Load dataset
    dataset = tf.keras.utils.image_dataset_from_directory(
        image_folder_path,
        image_size=(224, 224),
        labels=None,
        label_mode="categorical",
        batch_size=1,
        shuffle=True,
    )

    ru1 = getrusage(RUSAGE_SELF).ru_maxrss

    # Load model
    json_file = open(model_file, "r")
    loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)
    json_file.close()

    # Load weights into new model
    loaded_model.load_weights(weights_file)
    print_and_log("Loaded model from disk!")

    ru2 = getrusage(RUSAGE_SELF).ru_maxrss

    print_and_log(loaded_model.summary())

    mfile_size = os.path.getsize(model_file)
    wfile_size = os.path.getsize(weights_file)

    print_and_log(f"Size of model json file ({model_file}): {mfile_size} bytes")
    print_and_log(f"Size of weights file ({weights_file}): {wfile_size} bytes")
    print_and_log(
        f"Memory used for the entire model loading process: {ru2 - ru1} {r_mem_units_str}."
    )

    total_elapsed_time = 0.0
    total_inference_memory = 0.0
    num_samples = len(dataset)
    print_and_log(f"Running inference on {num_samples} samples...")

    for image in dataset:
        # Input validation
        image_np = image.numpy()
        print(image_np.shape)
        if image_np.shape[-1] == 3:
            print_and_log("Model - Input Validation Okay - RGB image loaded")
        else: 
            print_and_log(f"Model - Input Validation Error - RGB image expected but  has wrong number of channels")
            # Not sure if this is the best way to deal with the spec: "input specification it will generate the output "N/A"
            break
        # OOD
        r_avg = image_np[:, :, 0].mean()
        g_avg = image_np[:, :, 1].mean()
        b_avg = image_np[:, :, 2].mean()

        r_dist_lb = 51
        r_dist_ub = 171
        g_dist_lb = 5
        g_dist_ub = 141
        b_dist_lb = 40
        b_dist_ub = 142

        if r_avg < r_dist_lb or r_dist_ub < r_avg:
            print_and_log(
                "Model - Input OOD Error - Red channel out of expected range"
            )
        if g_avg < g_dist_lb or g_dist_ub < g_avg:
            print_and_log(
                "Model - Input OOD Error - Green channel out of expected range"
            )
        if b_avg < b_dist_lb or b_dist_ub < b_avg:
            print_and_log(
                "Model - Input OOD Error - Blue channel out of expected range"
            )

        # Do inference
        start = time.time()
        ru3 = getrusage(RUSAGE_SELF).ru_maxrss
        pred = loaded_model.predict(image)
        ru4 = getrusage(RUSAGE_SELF).ru_maxrss
        end = time.time()

        elapsed_time = end - start
        inference_memory = ru4 - ru3
        total_elapsed_time += elapsed_time
        total_inference_memory += inference_memory

        
        # Output validation
        if pred.shape[1] == 102:
            print_and_log(f"Model - Output Validation Pass - {pred.shape} - validated")
        else:
            print_and_log(f"Model - Output Validation Error - Output shape: {pred.shape}")
        
        # Get prediction
        probs = tf.nn.softmax(pred)
        predicted_class = tf.argmax(probs, axis=-1)
        confidence = tf.reduce_max(probs, axis=-1)

        if confidence[0] > 0.015:
            label = garden.label_dict[int(predicted_class[0])]
            print_and_log(f"Model - file: {image_folder_path} predicted to be {label} (class {predicted_class}) with confidence {confidence}")
        else:
            print_and_log(f"Model - Output Confidence Error - max class confidence of {confidence} too low")

    avg_elapsed_time = total_elapsed_time / num_samples
    avg_inference_memory = total_inference_memory / num_samples
    print_and_log("\n--- STATISTICS ---")
    print_and_log(
        "Average elapsed time per inference: {0:.5f} seconds".format(
            avg_elapsed_time
        )
    )
    print_and_log(
        "Average memory used per inference: {0:.5f} {1}.".format(
            avg_inference_memory, r_mem_units_str
        )
    )

    return avg_elapsed_time, avg_inference_memory, r_mem_units_str


# Run the script if called on its own.
if __name__ == "__main__":
    args = parse_args()
    image_folder = args.images
    model_file = args.model
    weights_file = args.weights

    run_model(image_folder, model_file, weights_file)
