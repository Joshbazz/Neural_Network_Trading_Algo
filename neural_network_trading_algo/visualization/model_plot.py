import os
from datetime import datetime
from keras.models import load_model
from tensorflow.keras.utils import plot_model
from IPython.display import Image, display

def save_and_visualize_model(model_path, img_dir='neural_network_trading_algo/visualization'):
    """
    Save the loaded model and visualize it as a PNG image.

    Parameters:
    - model: The Keras model to be visualized.
    - img_dir: The directory where the visualization image should be saved.
    """

    model = load_model(model_path)

    # Generate a timestamp for the model file
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # # Ensure the directory exists
    # os.makedirs(img_dir, exist_ok=True)

    # Use the directory of this script if img_dir is not provided
    if img_dir is None:
        img_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure the directory exists
    os.makedirs(img_dir, exist_ok=True)

    # # Define the image path
    # img_path = os.path.join(img_dir, f"model_{timestamp}.png")
    # print(img_path)

    # Define the image path
    img_path = os.path.join(img_dir, f"model_{timestamp}.png")
    print(img_path)

    # Plot the model and save it as a PNG image
    plot_model(
        model,
        to_file=img_path,
        show_shapes=True,
        show_dtype=False,
        show_layer_names=True,
        rankdir="TB",
        expand_nested=False,
        dpi=200,
        show_layer_activations=True,
        show_trainable=True
    )

    # Display the image
    img = Image(filename=img_path)
    display(img)
    print(f"Model visualization saved and displayed from {img_path}")

# # Example usage:
# model = 'models/2024_06_30_18_04_02_stock_price_prediction_model_epochs_50.keras'
# img_dir = '/Users/joshbazz/Desktop/Bootcamp/neural_network_trading_algo/neural_network_trading_algo/visualization'
# save_and_visualize_model(model, img_dir)
