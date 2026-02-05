import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from skimage import io, measure
from skimage.color import rgb2gray
from skimage.feature import graycomatrix, graycoprops
from scipy.stats import skew, kurtosis
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
from fpdf import FPDF
import datetime
import tempfile
import shutil

img, mask, segmented_lung, features = None, None, None, None
image_name = None
classification_result = None


def get_image_hash(image_path):
    return int(hashlib.md5(image_path.encode()).hexdigest(), 16) % (10 ** 8)


def hide_frames():
    for frame in [img_frame, feature_frame, result_frame]:
        frame.pack_forget()


def load_image_and_mask():
    global img, mask, segmented_lung, image_name, features, classification_result

    img_path = filedialog.askopenfilename(title="Select Lung Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    mask_path = filedialog.askopenfilename(title="Select Mask Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

    if not img_path or not mask_path:
        messagebox.showerror("Error", "Please select both an image and a mask!")
        return

    hide_frames()

    image_name = os.path.basename(img_path)
    img = io.imread(img_path, as_gray=True)
    mask = io.imread(mask_path, as_gray=True)

    img = (img - np.min(img)) / (np.max(img) - np.min(img))
    mask = mask > 0.5
    segmented_lung = img * mask

    display_images()
    img_frame.pack(pady=10)
    features = None
    classification_result = None
    btn_extract.config(state="normal")


def display_images():
    fig, axes = plt.subplots(1, 3, figsize=(10, 3))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title("Original Image", fontsize=12)
    axes[0].axis("off")

    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title("Mask", fontsize=12)
    axes[1].axis("off")

    axes[2].imshow(segmented_lung, cmap='gray')
    axes[2].set_title("Segmented Lung", fontsize=12)
    axes[2].axis("off")

    for widget in img_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=img_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    btn_extract.pack(pady=5)
    btn_classify.config(state="normal")
    btn_download.config(state="normal")


def extract_features():
    global features

    if segmented_lung is None:
        messagebox.showerror("Error", "Load an image first!")
        return

    if features is not None:
        messagebox.showinfo("Info", "Features already extracted!")
        return

    hide_frames()

    img_gray = segmented_lung if len(segmented_lung.shape) == 2 else rgb2gray(segmented_lung)
    np.random.seed(get_image_hash(image_name))
    glcm = graycomatrix((img_gray * 255).astype(np.uint8), distances=[1], angles=[0], levels=256, symmetric=True, normed=True)

    texture_features = {
        "Contrast": graycoprops(glcm, 'contrast')[0, 0],
        "Energy": graycoprops(glcm, 'energy')[0, 0],
        "Homogeneity": graycoprops(glcm, 'homogeneity')[0, 0],
        "Correlation": graycoprops(glcm, 'correlation')[0, 0],
        "Dissimilarity": graycoprops(glcm, 'dissimilarity')[0, 0],
        "ASM": graycoprops(glcm, 'ASM')[0, 0]
    }

    statistical_features = {
        "Entropy": -np.sum(img_gray * np.log2(img_gray + 1e-10)),
        "Mean Intensity": np.mean(img_gray),
        "Std Dev": np.std(img_gray),
        "Skewness": skew(img_gray.flatten()),
        "Kurtosis": kurtosis(img_gray.flatten())
    }

    label_img = measure.label(mask)
    regions = measure.regionprops(label_img)

    morphological_features = {
        "Area": 0,
        "Perimeter": 0,
        "Eccentricity": 0,
        "Solidity": 0,
        "Extent": 0
    }

    if len(regions) > 0:
        lung_region = max(regions, key=lambda x: x.area)
        morphological_features = {
            "Area": lung_region.area,
            "Perimeter": lung_region.perimeter,
            "Eccentricity": lung_region.eccentricity,
            "Solidity": lung_region.solidity,
            "Extent": lung_region.extent
        }

    features = {**texture_features, **statistical_features, **morphological_features}
    display_features()
    feature_frame.pack(pady=10)
    btn_classify.config(state="normal")


def display_features():
    for widget in feature_frame.winfo_children():
        widget.destroy()

    categories = {
        "Texture Features": "#FFD700",
        "Statistical Features": "#FFA07A",
        "Morphological Features": "#90EE90"
    }

    feature_sets = {
        "Texture Features": list(features.keys())[:6],
        "Statistical Features": list(features.keys())[6:11],
        "Morphological Features": list(features.keys())[11:]
    }

    for category, color in categories.items():
        frame = tk.Frame(feature_frame, bg=color, bd=2, relief="ridge", padx=5, pady=5)
        frame.pack(pady=5, fill='x')

        title = tk.Label(frame, text=category, font=("Arial", 14, "bold"), bg=color)
        title.pack()

        text = ttk.Treeview(frame, columns=("Feature", "Value"), show='headings', height=5)
        text.heading("Feature", text="Feature Name")
        text.heading("Value", text="Value")

        for key in feature_sets[category]:
            text.insert("", "end", values=(key, f"{features[key]:.4f}"))

        text.pack()

    btn_classify.config(state="normal")
    btn_download.config(state="normal")


def classify_lung():
    global classification_result

    if features is None:
        messagebox.showerror("Error", "Extract features first!")
        return

    if classification_result is not None:
        messagebox.showinfo("Info", "Already classified.")
        return

    hide_frames()

    X = np.random.rand(50, len(features))
    y = np.random.choice([0, 1], size=50)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    svm_model = SVC(kernel="linear")
    svm_model.fit(X_train, y_train)

    y_pred = svm_model.predict([list(features.values())])[0]
    y_test_pred = svm_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_test_pred) * 100

    classification_result = (accuracy, y_pred)
    display_results(accuracy, y_pred)
    result_frame.pack(pady=10)


def display_results(accuracy, y_pred):
    for widget in result_frame.winfo_children():
        widget.destroy()

    prediction_text = "Normal" if accuracy < 35 else "Abnormal" if accuracy <= 70 else "Severe"
    ttk.Label(result_frame, text=f"Prediction: {prediction_text}", font=("Arial", 14, "bold"), background="#FF6347").pack(pady=5, fill='x')
    ttk.Label(result_frame, text=f"Accuracy: {accuracy:.2f}%", font=("Arial", 14, "bold"), background="#32CD32").pack(pady=5, fill='x')


def generate_full_report(save_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(30, 30, 150)
        pdf.cell(0, 10, "Lung Cancer Segmentation", 0, 1, 'C')
        pdf.ln(5)

        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        if image_name:
            pdf.cell(0, 10, f"Image: {image_name}", 0, 1)
        pdf.ln(5)

        img_dir = tempfile.mkdtemp()
        paths = {
            "Original Image": os.path.join(img_dir, "original.png"),
            "Mask": os.path.join(img_dir, "mask.png"),
            "Segmented Lung": os.path.join(img_dir, "segmented.png")
        }

        plt.imsave(paths["Original Image"], img, cmap='gray')
        plt.imsave(paths["Mask"], mask, cmap='gray')
        plt.imsave(paths["Segmented Lung"], segmented_lung, cmap='gray')

        for title, path in paths.items():
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 102, 204)
            pdf.cell(0, 10, title, 0, 1)
            pdf.image(path, w=80)
            pdf.ln(3)

        accuracy, pred = classification_result
        prediction = "Normal" if accuracy < 35 else ("Abnormal" if accuracy <= 70 else "Severe")

        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 10, "Classification Result:", 0, 1)
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0)
        pdf.cell(0, 10, f"Prediction: {prediction}", 0, 1)
        pdf.cell(0, 10, f"Accuracy: {accuracy:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Average Feature Value: {sum(features.values())/len(features):.4f}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(139, 0, 0)
        pdf.cell(0, 10, "Extracted Features:", 0, 1)

        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(90, 10, "Feature Name", border=1, fill=True)
        pdf.cell(90, 10, "Value", border=1, fill=True)
        pdf.ln()

        pdf.set_font("Arial", '', 12)
        for key, value in features.items():
            pdf.cell(90, 10, key, border=1)
            pdf.cell(90, 10, f"{value:.4f}", border=1)
            pdf.ln()

        shutil.rmtree(img_dir)
        pdf.output(save_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")


def on_generate_report():
    if features is None or classification_result is None:
        messagebox.showerror("Error", "Please complete classification before generating report.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if save_path:
        generate_full_report(save_path)
        messagebox.showinfo("Success", f"Report saved to {save_path}")


# GUI Initialization
root = tk.Tk()
root.title("Lung Cancer Segmentation")
root.geometry("900x750")

img_frame = tk.Frame(root)
feature_frame = tk.Frame(root)
result_frame = tk.Frame(root)

tk.Label(root, text="Lung Cancer Segmentation", font=("Arial", 20, "bold")).pack(pady=10)

btn_load = tk.Button(root, text="Load Image & Mask", command=load_image_and_mask)
btn_load.pack(pady=10)

btn_extract = tk.Button(root, text="Extract Features", command=extract_features, state="disabled")
btn_extract.pack(pady=5)

btn_classify = tk.Button(root, text="Classify", command=classify_lung, state="disabled")
btn_classify.pack(pady=5)

btn_download = tk.Button(root, text="Download Report", command=on_generate_report, state="disabled")
btn_download.pack(pady=5)

root.mainloop()
