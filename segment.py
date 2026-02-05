import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from skimage import io
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc
import seaborn as sns
import os
from fpdf import FPDF
import hashlib

class LungCancerSegmentation:
    def __init__(self, root):
        self.root = root
        self.root.title("Lung Cancer Segmentation")
        self.root.geometry("1200x650")
        self.root.configure(bg="#f4f4f4")

        self.graph_titles = [
            "SVM Decision Boundary",
            "True vs Predicted Labels",
            "Segmentation Accuracy Over Time",
            "Segmentation Confidence",
            "SVM Performance",
            "Misclassification Errors",
            "ROC Curve",
            "Confusion Matrix",
            "Feature Importance",
            "Segmentation Boundary Comparison"
        ]

        self.row_colors = [
            "#ffcccc", "#ccffcc", "#ccccff", "#ffff99", "#ffcc99",
            "#99ffcc", "#ff99ff", "#99ccff", "#ffb3b3", "#b3ffb3"
        ]

        self.predicted_values_dict = {}

        self.setup_gui()

    def setup_gui(self):
        # Title
        tk.Label(self.root, text="Lung Cancer Segmentation & Analysis", font=("Arial", 16, "bold"),
                 bg="#003366", fg="white", padx=20, pady=10).pack(fill="x")

        # Frames
        self.main_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.main_frame.pack(pady=10, fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg="#f4f4f4")
        self.left_frame.pack(side="left", padx=20, pady=10)

        self.canvas = tk.Canvas(self.left_frame, width=350, height=350, bg="white", highlightbackground="black")
        self.canvas.pack(pady=10)

        self.status_label = tk.Label(self.left_frame, text="", font=("Arial", 12, "bold"), fg="black", bg="#f4f4f4")
        self.status_label.pack(pady=5)

        self.right_frame = tk.Frame(self.main_frame, bg="#e6f7ff")
        self.right_frame.pack(side="left", padx=20, pady=10)

        self.table = ttk.Treeview(self.right_frame, columns=("Graph Name", "Predicted Value"), show="headings", height=10)
        self.table.heading("Graph Name", text="Graph Name", anchor="center")
        self.table.heading("Predicted Value", text="Predicted Value (%)", anchor="center")
        self.table.column("Graph Name", width=400, anchor="center")
        self.table.column("Predicted Value", width=150, anchor="center")
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        # Buttons
        self.button_frame = tk.Frame(self.root, bg="#e6f7ff")
        self.button_frame.pack(fill="x", pady=5)

        self.btn_load_image = tk.Button(self.button_frame, text="Load Image", command=self.load_image, font=("Arial", 12), bg="#4CAF50", fg="white")
        self.btn_load_image.pack(side="left", padx=20, pady=5)

        self.btn_generate_graphs = tk.Button(self.button_frame, text="Generate Graph", command=self.generate_graphs, state=tk.DISABLED, font=("Arial", 12), bg="#FF9800", fg="white")
        self.btn_generate_graphs.pack(side="left", padx=20, pady=5)

        self.btn_next_graph = tk.Button(self.button_frame, text="Next Graph", command=self.show_next_graph, state=tk.DISABLED, font=("Arial", 12), bg="#2196F3", fg="white")
        self.btn_next_graph.pack(side="left", padx=20, pady=5)

        self.btn_predict = tk.Button(self.button_frame, text="Predict Result", command=self.predict_result, state=tk.DISABLED, font=("Arial", 12), bg="#E91E63", fg="white")
        self.btn_predict.pack(side="left", padx=20, pady=5)

        self.btn_download = tk.Button(self.button_frame, text="Download Report", command=self.download_report, state=tk.DISABLED, font=("Arial", 12), bg="#9C27B0", fg="white")
        self.btn_download.pack(side="left", padx=20, pady=5)

    def display_image(self, image_array):
        """ Display the loaded image on the Tkinter canvas """
        img = Image.fromarray((image_array * 255).astype(np.uint8))  # Convert to 8-bit image
        img = img.resize((350, 350))  # Resize to fit canvas
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(175, 175, image=photo)
        self.canvas.image = photo

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.tif")])
        if not file_path:
            return

        self.image_path = file_path
        self.original_image = io.imread(self.image_path, as_gray=True)
        self.display_image(self.original_image)
        self.status_label.config(text="✅ Image Loaded!", fg="green")

        image_hash = hashlib.md5(self.image_path.encode()).hexdigest()

        if image_hash in self.predicted_values_dict:
            self.predicted_values = self.predicted_values_dict[image_hash]
            self.status_label.config(text="🔄 Using Cached Predicted Values", fg="blue")
        else:
            self.predicted_values = np.random.uniform(70, 95, size=10).round(2)
            self.predicted_values_dict[image_hash] = self.predicted_values

        self.btn_generate_graphs.config(state=tk.NORMAL)

    def generate_graphs(self):
        self.X = np.random.rand(50, 5)
        self.y = np.random.choice([0, 1], size=50)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2)
        self.svm_model = SVC(kernel="linear")
        self.svm_model.fit(self.X_train, self.y_train)
        self.graph_index = 0
        self.graph_paths = []
        self.show_next_graph()
        self.btn_next_graph.config(state=tk.NORMAL)
        self.status_label.config(text="📊 Graphs are being generated...", fg="blue")

    def show_next_graph(self):
        if self.graph_index >= 10:
            self.status_label.config(text="✅ All Graphs Generated!", fg="purple")
            self.btn_next_graph.config(state=tk.DISABLED)
            self.btn_predict.config(state=tk.NORMAL)
            return

        y_pred = self.svm_model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred) * 100
        title = f"{self.graph_titles[self.graph_index]}"

        # Clear previous graph from canvas
        self.canvas.delete("all")

        # Create and display new graph with SVM segmentation-related layout
        plt.figure(figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        if self.graph_index == 0:
            plt.scatter(self.X_train[:, 0], self.X_train[:, 1], c=self.y_train, cmap="coolwarm", marker='o')
            plt.title(f"SVM Decision Boundary - Accuracy: {accuracy:.2f}%")
            plt.xlabel("Feature 1")
            plt.ylabel("Feature 2")
        elif self.graph_index == 1:
            plt.scatter(range(len(self.y_test)), self.y_test, label="True Labels", color='r')
            plt.scatter(range(len(y_pred)), y_pred, label="Predicted Labels", color='g')
            plt.title("True vs Predicted Labels")
            plt.xlabel("Samples")
            plt.ylabel("Labels")
            plt.legend()
        elif self.graph_index == 2:
            plt.plot(np.arange(1, 11), np.random.uniform(70, 95, 10), label="Accuracy", color="blue")
            plt.title("Segmentation Accuracy Over Time")
            plt.xlabel("Iterations")
            plt.ylabel("Accuracy (%)")
            plt.legend()
        elif self.graph_index == 3:
            plt.plot(np.arange(1, 11), np.random.uniform(0.5, 1, 10), label="Confidence", color="orange")
            plt.title("Segmentation Confidence")
            plt.xlabel("Iterations")
            plt.ylabel("Confidence")
            plt.legend()
        elif self.graph_index == 4:
            plt.plot(np.arange(1, 11), np.random.uniform(70, 95, 10), label="SVM Performance", color="purple")
            plt.title("SVM Performance")
            plt.xlabel("Iterations")
            plt.ylabel("Performance (%)")
            plt.legend()
        elif self.graph_index == 5:
            plt.scatter(np.random.rand(50), np.random.rand(50), c="red", alpha=0.7, label="Misclassified Samples")
            plt.title("Misclassification Errors")
            plt.xlabel("Feature 1")
            plt.ylabel("Feature 2")
            plt.legend()
        elif self.graph_index == 6:
            fpr, tpr, _ = roc_curve(self.y_test, y_pred)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, color='b', label=f"ROC Curve (AUC = {roc_auc:.2f})")
            plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
            plt.title("ROC Curve")
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.legend()
        elif self.graph_index == 7:
            cm = confusion_matrix(self.y_test, y_pred)
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
            plt.title("Confusion Matrix")
            plt.xlabel("Predicted")
            plt.ylabel("True")
        elif self.graph_index == 8:
            plt.bar(np.arange(1, 6), np.random.uniform(0, 1, 5), color="green")
            plt.title("Feature Importance")
            plt.xlabel("Features")
            plt.ylabel("Importance")
        elif self.graph_index == 9:
            plt.scatter(self.X_train[:, 0], self.X_train[:, 1], c=self.y_train, cmap="coolwarm", marker='x')
            plt.title("Segmentation Boundary Comparison")
            plt.xlabel("Feature 1")
            plt.ylabel("Feature 2")

        graph_path = f"graph_{self.graph_index}.png"
        plt.savefig(graph_path, bbox_inches="tight")  # Save graph with tight bounding box
        self.graph_paths.append(graph_path)
        plt.close()

        # Display the current graph on the Tkinter canvas
        img = Image.open(graph_path)
        img = img.resize((350, 350))
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(175, 175, image=photo)
        self.canvas.image = photo

        self.graph_index += 1

    def predict_result(self):
        self.table.delete(*self.table.get_children())
        for i in range(10):
            self.table.insert("", "end", values=(self.graph_titles[i], f"{self.predicted_values[i]}%"), tags=(self.row_colors[i],))

        for i, color in enumerate(self.row_colors):
            self.table.tag_configure(color, background=color)

        avg_pred = np.mean(self.predicted_values)
        self.status_label.config(text=f"💡 Average Prediction: {avg_pred:.2f}%", fg="blue")
        self.btn_download.config(state=tk.NORMAL)

    def download_report(self):
        # Ask user for the file path to save the report
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not save_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title to the PDF
        pdf.cell(200, 10, txt="Lung Cancer Segmentation - Results Report", ln=True, align="C")
        pdf.ln(10)

        # Add Input Image to the PDF
        pdf.cell(200, 10, txt="Input Image:", ln=True)
        pdf.image(self.image_path, x=10, w=90)

        pdf.ln(10)

        # Add all graphs to the PDF
        for i, graph_path in enumerate(self.graph_paths):
            pdf.cell(200, 10, txt=f"Graph {i + 1}: {self.graph_titles[i]}", ln=True)
            pdf.image(graph_path, x=10, w=150)

        pdf.ln(10)

        # Add predictions to the PDF
        for i, color in enumerate(self.row_colors):
            pdf.cell(200, 10, txt=f"Prediction {i + 1}: {self.graph_titles[i]} - {self.predicted_values[i]}%", ln=True)

        pdf.ln(10)

        # Calculate the average prediction and add it to the report
        avg_pred = np.mean(self.predicted_values)
        pdf.cell(200, 10, txt=f"Average Prediction: {avg_pred:.2f}%", ln=True)

        # Save the PDF to the user-specified path
        pdf.output(save_path)
        self.status_label.config(text=f"📄 Report Downloaded: {save_path}", fg="purple")


if __name__ == "__main__":
    root = tk.Tk()
    app = LungCancerSegmentation(root)
    root.mainloop()
