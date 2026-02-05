import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from skimage import io, filters, morphology
from skimage.segmentation import active_contour
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from datetime import datetime


class LungSegmentationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lung Image Segmentation")
        self.root.geometry("800x600")

        # Buttons
        self.btn_load = tk.Button(root, text="Load Image", command=self.load_image)
        self.btn_load.pack(pady=10)

        self.btn_otsu = tk.Button(root, text="Apply Otsu Thresholding", command=self.apply_otsu, state=tk.DISABLED)
        self.btn_otsu.pack(pady=5)

        self.btn_snake = tk.Button(root, text="Apply Active Contour", command=self.apply_snake, state=tk.DISABLED)
        self.btn_snake.pack(pady=5)

        # Changed button text to Download Report
        self.btn_report = tk.Button(root, text="Download Report", command=self.generate_report, state=tk.DISABLED)
        self.btn_report.pack(pady=5)

        # Canvas for displaying images
        self.canvas = tk.Canvas(root, width=512, height=512)
        self.canvas.pack(pady=10)

        self.image_path = None
        self.original_image = None
        self.otsu_result = None
        self.snake_result = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.tif")])
        if not file_path:
            return

        self.image_path = file_path
        self.original_image = io.imread(self.image_path, as_gray=True)

        # Display Original Image
        self.display_image(self.original_image)
        self.btn_otsu.config(state=tk.NORMAL)
        self.btn_report.config(state=tk.DISABLED)

    def apply_otsu(self):
        if self.original_image is None:
            return

        # Apply Otsu's thresholding
        threshold = filters.threshold_otsu(self.original_image)
        otsu_mask = self.original_image > threshold

        # Remove small noise
        otsu_mask = morphology.remove_small_objects(otsu_mask, min_size=500)
        otsu_mask = morphology.remove_small_holes(otsu_mask, area_threshold=500)

        # Store result for report
        self.otsu_result = otsu_mask

        # Display result
        self.display_image(otsu_mask)
        self.btn_snake.config(state=tk.NORMAL)

    def apply_snake(self):
        if self.original_image is None:
            return

        # Create an initial contour around the lung region
        s = np.linspace(0, 2 * np.pi, 400)
        x = self.original_image.shape[1] // 2 + 100 * np.cos(s)
        y = self.original_image.shape[0] // 2 + 100 * np.sin(s)
        init_contour = np.array([x, y]).T

        # Apply active contour model
        snake = active_contour(self.original_image, init_contour, alpha=0.01, beta=0.1, gamma=0.001)

        # Store result for report
        fig = plt.figure(figsize=(5, 5))
        plt.imshow(self.original_image, cmap='gray')
        plt.plot(snake[:, 0], snake[:, 1], '-r', lw=2)
        plt.title("Active Contour Model (Snake)")
        plt.axis('off')

        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        snake_path = os.path.join(temp_dir, "snake_result.png")
        plt.savefig(snake_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        self.snake_result = snake_path

        # Display result
        plt.imshow(self.original_image, cmap='gray')
        plt.plot(snake[:, 0], snake[:, 1], '-r', lw=2)
        plt.title("Active Contour Model (Snake)")
        plt.show()

        self.btn_report.config(state=tk.NORMAL)

    def display_image(self, image_array):
        image = (image_array * 255).astype(np.uint8)
        image = Image.fromarray(image)
        image = image.resize((512, 512))
        photo = ImageTk.PhotoImage(image)

        self.canvas.create_image(256, 256, image=photo)
        self.canvas.image = photo  # Keep a reference

    def generate_report(self):
        if not all([self.original_image is not None, self.otsu_result is not None, self.snake_result is not None]):
            return

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Colors
        title_color = (0, 102, 204)  # Blue
        section_color = (0, 153, 76)  # Green
        text_color = (50, 50, 50)  # Dark gray

        # Title
        pdf.set_text_color(*title_color)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 10, "Lung Image Segmentation Report", ln=True, align='C')
        pdf.ln(8)

        # Date and time
        pdf.set_text_color(*text_color)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)

        # Save original image
        orig_path = os.path.join(tempfile.gettempdir(), "original_temp.png")
        Image.fromarray((self.original_image * 255).astype(np.uint8)).save(orig_path)

        # Section: Original Image
        pdf.set_text_color(*section_color)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "1. Original Lung Image", ln=True)
        pdf.ln(4)

        pdf.image(orig_path, w=150)
        pdf.ln(8)

        # Save Otsu image
        otsu_path = os.path.join(tempfile.gettempdir(), "otsu_temp.png")
        Image.fromarray(self.otsu_result.astype(np.uint8) * 255).save(otsu_path)

        # Section: Otsu Thresholding
        pdf.set_text_color(*section_color)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "2. Otsu Thresholding Segmentation", ln=True)
        pdf.ln(4)

        pdf.image(otsu_path, w=150)
        pdf.ln(8)

        # Section: Active Contour
        pdf.set_text_color(*section_color)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "3. Active Contour Segmentation", ln=True)
        pdf.ln(4)

        pdf.image(self.snake_result, w=150)
        pdf.ln(10)

        # Final Remarks
        pdf.set_text_color(255, 51, 51)  # Red color
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Segmentation Completed Successfully!", ln=True, align='C')

        # Save the PDF
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="Lung_Segmentation_Report.pdf"
        )

        if save_path:
            pdf.output(save_path)

        # Clean up temp files
        os.remove(orig_path)
        os.remove(otsu_path)
        os.remove(self.snake_result)


# Run the Tkinter App
root = tk.Tk()
app = LungSegmentationApp(root)
root.mainloop()
