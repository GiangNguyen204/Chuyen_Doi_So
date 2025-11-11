
<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
   🚀 Web Game Lịch Sử Điện Biên Phủ (1954)
</h2>
<div align="center">
    <p align="center">
        <img width="170"  alt="AIoTLab Logo" src="https://github.com/user-attachments/assets/722ef6fe-9b09-41f4-9d58-a752e2be9da4" />
        <img width="180"  alt="FIT DNU Logo" src="https://github.com/user-attachments/assets/38f342e5-4c81-4d22-b1d0-985cf91c702c" />
        <img width="200"  alt="DaiNam University" src="https://github.com/user-attachments/assets/11138726-5355-4c53-9fdb-bec177681ae0" />
    </p>

<div align="center">

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

</div>

---

## 1. Giới thiệu hệ thống

Đây là **web game lịch sử tương tác** về **Chiến dịch Điện Biên Phủ (1954)**, được phát triển nhằm đổi mới phương pháp học lịch sử thông qua trò chơi hoá (gamification) và công nghệ web thời gian thực.

### 🎯 Mục tiêu chính
- Giúp người học **hiểu và ghi nhớ** chuỗi sự kiện của chiến dịch Điện Biên Phủ.  
- Tăng cường **trải nghiệm học tập sinh động** với âm thanh, hình ảnh, câu hỏi tương tác.  
- Khuyến khích **thi đua lành mạnh** thông qua bảng xếp hạng trực tuyến (Leaderboard).

### 🧩 Các tính năng nổi bật
- 🔐 **Đăng nhập bằng Google (Firebase Auth)**  
  Xác thực nhanh, lưu danh tính và tiến độ học.
- ☁️ **Lưu trữ điểm & xếp hạng trên Cloud Firestore**  
  Đồng bộ dữ liệu thời gian thực, hiển thị top người chơi toàn cầu.
- 🔊 **Thuyết minh tự động (Web Speech API)**  
  Giọng đọc tiếng Việt tự động giúp người học ghi nhớ hiệu quả.
- ❓ **Câu hỏi tương tác, gợi ý và 50:50**  
  Mỗi mốc sự kiện gắn với một câu hỏi trắc nghiệm bốn lựa chọn.
- ⏱ **Giới hạn thời gian 20 giây**  
  Thanh tiến độ hiển thị thời gian và phần trăm hoàn thành.
- 🎇 **Pháo hoa Grand Finale**  
  Khi người chơi đạt điểm tuyệt đối, hệ thống kích hoạt hiệu ứng pháo hoa toàn màn hình!

---

## ⚙️ 2. Công nghệ sử dụng

### 💻 Frontend
- **HTML5 / CSS3 / Tailwind CSS** – thiết kế responsive, hiện đại.  
- **JavaScript (ES6+)** – điều khiển logic game, tính điểm, timer.

### ☁️ Dịch vụ nền tảng
- **Firebase Authentication** – đăng nhập bằng Google.  
- **Cloud Firestore** – lưu dữ liệu điểm, thứ hạng, và thông tin người chơi.

### 🔊 Tính năng đa phương tiện
- **Web Speech API** – thuyết minh sự kiện bằng tiếng Việt.  
- **canvas-confetti** – tạo hiệu ứng pháo hoa rực rỡ khi chiến thắng.

### 📚 Thư viện hỗ trợ
- `firebase-app-compat.js`, `firebase-auth-compat.js`, `firebase-firestore-compat.js`
- `tailwindcss CDN`
- `canvas-confetti`

---

## 3. Một số hình ảnh hệ thống

<p align="center">
    <em>Màn hình đăng nhập với Google Sign-in</em><br/>
    <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/eb8feace-4ca3-41ac-8159-59a557b7ad71" />

</p>

<p align="center">
    <em>Giao diện màn chơi chính: ảnh sự kiện, câu hỏi, điểm và leaderboard</em><br/>
    <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/e55fddd3-2b25-4a44-88d7-ea7de650dac5" />

</p>

<p align="center">
    <em>Lưới 10 mốc sự kiện Điện Biên Phủ</em><br/>
  <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/68537ee7-8795-419f-9702-6782e74a9269" />
  <img src="docs/eventgrid_dienbien.png" width="850" alt="Event Grid"/>
</p>

<p align="center">
    <em>Pháo hoa Grand Finale khi người chơi đạt điểm tuyệt đối</em><br/>
    <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/9d0e9f11-507b-4042-bd5e-a976452b2a77" />

</p>

---

## 🛠️ 4. Hướng dẫn cài đặt & triển khai

### 4.1. Yêu cầu hệ thống
- 🌐 Trình duyệt hỗ trợ **ES6 + Web Speech API** (Chrome/Edge/Firefox).  
- ☁️ Tài khoản Firebase đã kích hoạt Auth và Firestore.  
- 💻 Không cần server backend – chỉ cần web server tĩnh.

---

### 📦 4.2. Clone dự án

```bash
git clone https://github.com/<username>/<repo-dien-bien-phu-webgame>.git
cd <repo-dien-bien-phu-webgame>
```

---

### 🔧 4.3. Cấu hình Firebase

1. Truy cập [Firebase Console](https://console.firebase.google.com/).  
2. Tạo Project mới → Bật **Authentication** (phương thức Google).  
3. Mở **Cloud Firestore** → Chọn “Start in test mode”.  
4. Tạo Web App và copy đoạn cấu hình sau:

```js
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

5. Dán đoạn trên vào file `firebase-config.js` trong dự án.  
6. Cấu hình **Firestore Rules**:

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /scores/{document=**} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if false;
    }
  }
}
```

---

### ▶️ 4.4. Chạy ứng dụng

#### 🔹 Cách 1: Dùng VS Code + Live Server
1. Mở thư mục dự án bằng Visual Studio Code.  
2. Cài extension **Live Server**.  
3. Nhấp chuột phải vào `index.html` → “Open with Live Server”.  
4. Trình duyệt sẽ mở tại `http://localhost:5500`.

#### 🔹 Cách 2: Dùng Python HTTP Server
```bash
python -m http.server 8000
```
Mở trình duyệt tại [http://localhost:8000](http://localhost:8000)

---

### ✅ 4.5. Kiểm tra hoạt động
1. Truy cập `index.html`.  
2. Nhấn “Đăng nhập bằng Google”.  
3. Chọn một mốc sự kiện để nghe thuyết minh và trả lời câu hỏi.  
4. Sau khi hoàn tất, kiểm tra bảng xếp hạng Firestore cập nhật tự động.  
5. Nếu đạt điểm tối đa, quan sát hiệu ứng **pháo hoa Grand Finale**.

---

## 📞 5. Liên hệ

- 📧 **Email:** giangnguyen27112k4@gmail.com  
- 📞 **SĐT:** 0353397306  
- 🌐 **Facebook:** [Giang Nguyen](https://www.facebook.com/jannguyen04)

---

<p align="center">
✨ <em>README này được thiết kế bởi Giang Nguyen cho dự án Web Game Lịch Sử Điện Biên Phủ (1954) — một phần của BTL Chuyển đổi số Trường Đại học Đại Nam.</em>
</p>
