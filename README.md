
# 🖼️ Image Generation Project  

An AI-powered image generation project using APIs and Gradio for an interactive interface. Built with Python and Requests.  

---

## 🚀 **Features**  
- Generate images by providing a description and choosing a style.  
- Save generated images locally.  
- Upload an existing image to generate a prompt describing it.  
- Use the generated prompt to create new images in different styles.  

---

## 🛠️ **Setup Instructions**  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/LexViper/Image_Generation.git
   cd Image_Generation
   ```

2. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create an account on Hugging Face:**  
   - Visit [Hugging Face](https://huggingface.co/) and create an account.  
   - Go to your profile settings and create an API token.  
   - Copy the token and save it.  

4. **Add your API token to the project:**  
   - Create a `.env` file in the project directory.  
   - Add the following line:  
     ```
     HUGGINGFACE_API_KEY=your_token_here
     ```

---

## 💻 **How to Run**  
1. Start the Gradio interface:  
   ```bash
   python images.py or images.ipynb
   ```  
2. Open the local link provided by Gradio in your browser.  

---

## ✨ **How to Use**  

### **Image Generation:**  
- Paste your API token in the interface.  
- Enter a description of the image you want to generate.  
- Choose a style from the list (e.g., Anime, Realistic, Cartoon).  
- Click "Generate" and wait for the image to appear.  
- Save the image using the "Download" button.  

### **Image Transformation:**  
- Upload an image of yourself or any other photo.  
- The app will generate a description (prompt) of the image.  
- Use the prompt to generate a new image in the chosen style.  

---

## 🌐 **Demo**  

Check out the working demo below:  

![Demo Screenshot](https://github.com/LexViper/Image_Generation/raw/main/Images/Interface%20v1.png)  

---

## 📂 **Project Structure**  
- `images.py`: Main script to run the Gradio interface.  
- `requirements.txt`: Python dependencies.  
- `README.md`: Project documentation.  

---

## 👥 **Contributors**  
Big thanks to the following awesome people who helped make this project happen:  
- [Harsh Pandit](https://github.com/ItsHarsh-Pandit)  
- [Aryan Kaminwar](https://github.com/ARI-create193)  

---

## 📧 **Contact**  

For any queries or suggestions, reach out at thisisabhay.c@gmail.com  



