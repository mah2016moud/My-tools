import os
import sys
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")
import threading 
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from rembg import remove, new_session
from PIL import Image


def process_image():
    file_path = filedialog.askopenfilename(
        title="إختر صورة لقص خلفيتها",
        filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
    )
    if not file_path: return

   
    threading.Thread(target=run_removal, args=(file_path,), daemon=True).start()

def run_removal(file_path):
    try:
        
        progress_bar.pack(pady=10)
        progress_bar.start(2) 
        status_label.config(text="⏳ جاري المعالجة (قد يستغرق وقتاً في المرة الأولى)...", fg="#f39c12")
        select_btn.config(state="disabled") 

        selected_mode = mode_combo.get()
        model_name = 'u2net'
        if selected_mode == "أشخاص (دقة عالية)": model_name = 'u2net_human_seg'
        
        session = new_session(model_name)

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(application_path, f"{base_name}_{model_name}_no_bg.png")

        input_image = Image.open(file_path)
        output_image = remove(input_image, session=session)
        output_image.save(output_path)

      
        status_label.config(text="✅ تم الحفظ بنجاح!", fg="#27ae60")
        messagebox.showinfo("نجاح", f"تم الحفظ بجانب البرنامج باسم:\n{os.path.basename(output_path)}")
        
    except Exception as e:
        status_label.config(text="❌ حصل خطأ", fg="#c0392b")
        messagebox.showerror("خطأ", f"المشكلة: {e}")
    
    finally:
        
        progress_bar.stop()
        progress_bar.pack_forget()
        select_btn.config(state="normal")

root = tk.Tk()
root.title("Advanced BG Remover v2.5")
root.geometry("450x500") 
root.configure(bg="#f4f6f7")

header = tk.Label(root, text="برنامج إزالة الخلفية .", bg="#2c3e50", fg="white", 
                 font=("Arial", 16, "bold"), pady=20)
header.pack(fill="x")

tk.Label(root, text="إختر نوع القص (الموديل):", bg="#f4f6f7", font=("Arial", 11)).pack(pady=(20, 5))
mode_combo = ttk.Combobox(root, values=["عام (تلقائي)", "أشخاص (دقة عالية)",], state="readonly", width=25)
mode_combo.current(0)
mode_combo.pack(pady=5)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"))
select_btn = ttk.Button(root, text="إختر الصورة وابدأ", command=process_image)
select_btn.pack(pady=20)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")

status_label = tk.Label(root, text="جاهز للعمل", bg="#f4f6f7", font=("Arial", 11, "bold"))
status_label.pack(pady=10)

footer_frame = tk.Frame(root, bg="#f4f6f7")
footer_frame.pack(side="bottom", fill="x", pady=10)

line = tk.Canvas(footer_frame, height=1, bg="#bdc3c7", highlightthickness=0)
line.pack(fill="x", padx=50, pady=5)

copyright_label = tk.Label(
    footer_frame, 
    text="© 2026 | All Rights Reserved\nMAHMOUD ABDALLA", 
    font=("Arial", 9, "bold"),
    fg="#7f8c8d",
    bg="#f4f6f7",
    justify="center"
)
copyright_label.pack()
messagebox.showinfo("ترحيب", "أهلاً بك  .\n\nيرجى التأكد من توفر إنترنت عند تشغيل البرنامج لأول مرة فقط لضمان تحميل موديلات الذكاء الاصطناعي بنجاح.")
root.mainloop()