import os
from datetime import datetime
from keras.models import load_model
from tensorflow.keras.utils import plot_model
from IPython.display import Image, display

def save_and_visualize_model(model, img_dir):
    """
    Save the loaded model and visualize it as a PNG image.

    Parameters:
    - model: The Keras model to be visualized.
    - img_dir: The directory where the visualization image should be saved.
    """

    # Generate a timestamp for the model file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Ensure the directory exists
    os.makedirs(img_dir, exist_ok=True)

    # Define the image path
    img_path = os.path.join(img_dir, f"model_{timestamp}.png")

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

# Example usage:
model = load_model('models/stock_price_prediction_model.keras')
img_dir = 'visualizations'
save_and_visualize_model(model, img_dir)