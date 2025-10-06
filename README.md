# 📸 Instagram Clone (Django REST Framework)

**Instagram Clone** — bu foydalanuvchilar ro‘yxatdan o‘tib, post joylay oladigan, like bosadigan va sharh yozadigan ijtimoiy tarmoq ilovasi.  
Loyiha **Django REST Framework** asosida yaratilgan bo‘lib, real Instagram’ning asosiy funksiyalarini backend darajasida takrorlaydi.

---

## 🚀 Xususiyatlar

- 🔐 Foydalanuvchi ro‘yxatdan o‘tishi va tizimga kirishi (JWT Auth)
- 👤 Profil ma’lumotlarini ko‘rish va tahrirlash
- 🖼 Postlar yaratish, o‘chirish va tahrirlash
- ❤️ Like bosish / bekor qilish
- 💬 Sharh (comment) qoldirish
- 👥 Foydalanuvchini kuzatish (follow/unfollow)
- 🧩 Modulli arxitektura (`user`, `post`, `shared`)

---

## 🛠 Texnologiyalar

- **Backend:** Django, Django REST Framework  
- **Autentifikatsiya:** Simple JWT  
- **Database:** SQLite / PostgreSQL  
- **Media storage:** Django Media  
- **API Test:** Postman / Swagger  

---

## ⚙️ O‘rnatish bo‘yicha yo‘riqnoma

1. Loyihani klonlash:
   ```bash
   git clone https://github.com/<username>/instagram-clone.git
   cd instagram-clone
   ```

2. Virtual muhit yaratish:
   ```bash
   python -m venv venv
   source venv/bin/activate    # Mac/Linux
   venv\Scripts\activate       # Windows
   ```

3. Kerakli kutubxonalarni o‘rnatish:
   ```bash
   pip install -r requirements.txt
   ```

4. Migratsiyalarni bajarish:
   ```bash
   python manage.py migrate
   ```

5. Serverni ishga tushurish:
   ```bash
   python manage.py runserver
   ```

---

## 🧠 Asosiy API endpointlar

| Endpoint | Metod | Tavsif |
|-----------|--------|--------|
| `/api/users/register/` | POST | Ro‘yxatdan o‘tish |
| `/api/users/login/` | POST | Tizimga kirish |
| `/api/posts/` | GET / POST | Postlar ro‘yxati yoki yangi post |
| `/api/posts/<id>/` | GET / PUT / DELETE | Bitta post bilan ishlash |
| `/api/posts/<id>/like/` | POST | Postga like bosish |
| `/api/comments/` | POST | Sharh qoldirish |

---

## 📦 Papkalar tuzilmasi

```
instagram-clone/
├── user/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── post/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── shared/
│   ├── utils.py
│   └── permissions.py
├── config/
│   └── settings.py
└── manage.py
```

---

## 👨‍💻 Muallif

**Shahzod Ravshanov**  
📧 [shahzodravshanov1234@gmail.com]  
💻 Backend Developer (Django / DRF / Python)

---


